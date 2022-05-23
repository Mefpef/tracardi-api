import logging
from time import sleep
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from app.config import server
from elasticsearch import ElasticsearchException

from tracardi.config import tracardi
from tracardi.domain.credentials import Credentials
from tracardi.domain.mapping import Mapping
from tracardi.domain.user import User
from tracardi.exceptions.exception import StorageException
from tracardi.exceptions.log_handler import log_handler
from tracardi.service.setup.setup_indices import create_indices
from tracardi.service.setup.setup_plugins import add_plugins
from tracardi.service.storage.driver import storage
from tracardi.service.storage.index import resources
from tracardi.service.storage.indices_manager import get_indices_status, remove_index

router = APIRouter()
logger = logging.getLogger(__name__)
logger.setLevel(tracardi.logging_level)
logger.addHandler(log_handler)


@router.get("/install", tags=["installation"], include_in_schema=server.expose_gui_api, response_model=dict)
async def check_if_installation_complete():
    """
    Returns list of missing and updated indices
    """
    try:

        # Missing indices

        _indices = [item async for item in get_indices_status()]
        missing_indices = [idx[1] for idx in _indices if idx[0] == 'missing_index']
        existing_indices = [idx[1] for idx in _indices if idx[0] == 'existing_index']
        missing_templates = [idx[1] for idx in _indices if idx[0] == 'missing_template']
        missing_aliases = [idx[1] for idx in _indices if idx[0] == 'missing_alias']
        # existing_templates = [idx[1] for idx in _indices if idx[0] == 'existing_template']

        # Missing admin

        index = resources.get_index('user')

        if index.get_aliased_data_index() in existing_indices:
            admins = await storage.driver.user.search_by_role('admin')
            admins = admins.dict()
        else:
            admins = {
                "total": 0,
                "result": []
            }

        try:
            current_mappings = await storage.driver.mapping.load_all()
            mappings = {mapping['index_name']: Mapping(**mapping) for mapping in current_mappings}
        except StorageException:
            mappings = {}

        # Missing mapping

        missing_mapping_setup = []

        for name, index_setup in resources.resources.items():
            if name not in mappings:
                missing_mapping_setup.append(name)

        return {
            "missing": missing_indices,
            "admins": admins,
            "missing_setup": missing_mapping_setup,
            "missing_template": missing_templates,
            "missing_alias": missing_aliases,
        }

    except ElasticsearchException as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/install/plugins", tags=["installation"], include_in_schema=server.expose_gui_api, response_model=dict)
async def install_plugins():
    try:
        return await add_plugins()
    except ElasticsearchException as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/install", tags=["installation"], include_in_schema=server.expose_gui_api, response_model=dict)
async def install(credentials: Optional[Credentials]):
    try:

        if server.reset_plugins is True:
            await remove_index('action')

        result = {"created": await create_indices(), 'admin': False}

        # Add admin
        admins = await storage.driver.user.search_by_role('admin')

        if admins.total == 0:
            if credentials.not_empty() and credentials.username_as_email():

                user = User(
                    id=credentials.username,
                    password=credentials.password,
                    roles=['admin'],
                    email=credentials.username,
                    full_name="Default Admin"
                )

                if not await storage.driver.user.check_if_exists(credentials.username):
                    await storage.driver.user.add_user(user)
                    logger.info("Default admin account created.")

                result['admin'] = True
        else:
            logger.warning("There is at least one admin account. New admin account not created.")
            result['admin'] = True

        if result['admin'] is True and server.update_plugins_on_start_up is not False:
            logger.info(f"Updating plugins on startup due to: UPDATE_PLUGINS_ON_STARTUP={server.update_plugins_on_start_up}")
            result['plugins'] = await add_plugins()

        return result

    except Exception as e:
        logger.error(f"Error on install. Reason: {str(e)}.")
        raise HTTPException(status_code=500, detail=str(e))
