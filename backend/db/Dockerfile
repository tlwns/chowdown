FROM postgres:alpine

COPY ./docker_init.sql ./docker-entrypoint-initdb.d
COPY ./schema.sql ./docker-entrypoint-initdb.d
