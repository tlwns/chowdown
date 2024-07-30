FROM postgres:16.2-alpine3.19

COPY ./docker_init.sql ./docker-entrypoint-initdb.d
COPY ./schema.sql ./docker-entrypoint-initdb.d
