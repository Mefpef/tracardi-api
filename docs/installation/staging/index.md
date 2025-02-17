# Staging server

A staging server is a type of server environment that is used to test and debug new code changes before they are
deployed to a production server. This allows developers to test and refine new features or bug fixes in a safe and
controlled environment, without impacting the performance or functionality of the live production website or
application. It also allows QA Team to test the application before it goes to the production. This helps ensure that the
code is stable and functioning properly before it is made available to end users. Overall, using a staging server helps
to minimize the risk of errors or disruptions in a live production environment, and helps to ensure the quality and
stability of the final product.

## Tracardi staging server deployment

The process of staging in Tracardi involves creating a separate copy of the system that is specifically designated as a
staging server. This is done by installing another copy of the system and setting the environment variable "PRODUCTION"
to "yes". This creates another set of indices in Elasticsearch that are prefixed with "prod-".

The production server should not be edited directly. Instead, all changes should be made on the staging server and
thoroughly tested before being deployed to the production system. This helps to minimize the risk of errors or
disruptions in the live production environment.

Once changes have been tested on the staging server, they can then be deployed to the production system. This is done by
copying the data from the staging server to the production server. However, certain data such as events, profiles, or
error logs will not be copied over during this process to ensure that the production server data remains intact.

## Staging server security and networking

The preferred settings for networking a staging server involve separating the staging and production servers by
assigning different API IP addresses. This is done for security reasons, as the staging server should not be exposed to
the internet and should only be accessible within the internal network, preferably through a VPN. This ensures that only
the production collector endpoints are publicly available.

Additionally, it is important to limit access to the production server by not having accounts with roles that allow
changes to the server configuration. The best practice is to have a single admin account and only marketing accounts
that can view data but not change any settings. This helps to prevent unauthorized access or changes that could
potentially disrupt the production environment.

## Licensing commercial version of Tracardi 

No need to worry about separate licenses for staging and production servers, all commercial licenses cover both.

# Summary

This documenation answers the following questions:

* How to test workflows?
* What is a staging server?
* What is the process of staging in Tracardi?
* How does Tracardi ensure the security of its staging server?
* Do I need a separate license for the staging server if I have a commercial version of Tracardi?
