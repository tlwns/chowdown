-- DreamTeam Schema
-- Original version: Chitrakshi Gosain (March 9 2024)
-- Current version: Chitrakshi Gosain (April 9 2024)
--
-- Some general naming principles:
--   max 16 chars in field names
--   all entity tables are named using plural nouns
--   for tables with unique numeric identifier, always call the field "id"
--   for foreign keys referring to an "id" field in the foreign relation,
--      use the singular-noun name of the relation as the field name
--      OR use the name of the relationship being represented
--
-- Null values:
--  for each relation, a collection of fields is identified as being
--    compulsory (i.e. without them the data isn't really usable) and
--    they are all defined as NOT NULL
--  reminder: all of the primary keys (e.g. "id") are non-NULL
--  note also that fields that are allowed to be NULL will need to be
--    handled specially whenever they are displayed e.g. in a web-based
--    interface to this schema;

DROP TYPE IF EXISTS PASS_TYPE CASCADE;
DROP TYPE IF EXISTS STATUS_TYPE CASCADE;
DROP TYPE IF EXISTS PERSON_NAME CASCADE;

DROP TABLE IF EXISTS fav_eateries CASCADE;
DROP TABLE IF EXISTS blocked_eateries CASCADE;
DROP TABLE IF EXISTS passwords CASCADE;
DROP TABLE IF EXISTS voucher_instances CASCADE;
DROP TABLE IF EXISTS keywords CASCADE;
DROP TABLE IF EXISTS vouchers CASCADE;
DROP TABLE IF EXISTS all_sessions CASCADE;
DROP TABLE IF EXISTS customers CASCADE;
DROP TABLE IF EXISTS preferences CASCADE;
DROP TABLE IF EXISTS eatery_details CASCADE;
DROP TABLE IF EXISTS reviews CASCADE;
DROP TABLE IF EXISTS reports CASCADE;
DROP TABLE IF EXISTS eateries CASCADE;
DROP TABLE IF EXISTS addresses CASCADE;
DROP TABLE IF EXISTS eatery_atoms CASCADE;
DROP TABLE IF EXISTS customer_likes CASCADE;

-- Types / Domains;

CREATE TYPE PASS_TYPE AS ENUM ('current', 'old');
CREATE TYPE STATUS_TYPE AS ENUM ('unpublished', 'unclaimed', 'claimed', 'redeemed', 'reserved');
CREATE TYPE SCHEDULE_TYPE AS ENUM ('daily', 'weekly', 'fortnightly', 'monthly');
CREATE TYPE PERSON_NAME AS (
    last_name VARCHAR(50),
    first_name VARCHAR(50)
);

-- Tables;

CREATE TABLE addresses (
    id                      BIGSERIAL,
    unit_number             VARCHAR(10),
    house_number            VARCHAR(10),
    street_addr             VARCHAR(255) NOT NULL,
    city                    VARCHAR(100) NOT NULL,
    state                   VARCHAR(100) NOT NULL,
    county                  VARCHAR(50) NOT NULL,
    country                 VARCHAR(50) NOT NULL,
    postcode                VARCHAR(10) NOT NULL,
    longitude               FLOAT NOT NULL,
    latitude                FLOAT NOT NULL,
    formatted_str           TEXT NOT NULL,
    PRIMARY KEY             (id)
);

CREATE TABLE eateries (
    id                      BIGSERIAL,
    eatery_name             VARCHAR(255) NOT NULL,
    is_deleted              BOOLEAN DEFAULT FALSE,
    PRIMARY KEY             (id)
);

CREATE TABLE eatery_details (
    email                   TEXT UNIQUE NOT NULL,
    phone_number            VARCHAR(20) UNIQUE NOT NULL,
    manager                 PERSON_NAME NOT NULL,
    abn                     VARCHAR(11) UNIQUE NOT NULL,
    date_joined             TIMESTAMP WITH TIME ZONE NOT NULL,
    description             TEXT,
    address                 BIGINT NOT NULL,
    thumbnail               TEXT DEFAULT '/eatery_thumbnail.webp',
    menu                    TEXT,
    eatery                  BIGINT UNIQUE NOT NULL,
    PRIMARY KEY             (eatery),
    FOREIGN KEY             (eatery) REFERENCES eateries(id),
    FOREIGN KEY             (address) REFERENCES addresses(id)
);

CREATE TABLE keywords (
    id                      BIGSERIAL,
    title                   VARCHAR(255) UNIQUE NOT NULL,
    PRIMARY KEY             (id)
);

CREATE TABLE eatery_atoms (
    keyword                 BIGINT,
    eatery                  BIGINT,
    PRIMARY KEY             (keyword, eatery),
    FOREIGN KEY             (keyword) REFERENCES keywords(id),
    FOREIGN KEY             (eatery) REFERENCES eateries(id)
);

CREATE TABLE customers (
    id                      BIGSERIAL,
    customer_name           PERSON_NAME NOT NULL,
    email                   TEXT UNIQUE NOT NULL,
    phone_number            VARCHAR(20) UNIQUE NOT NULL,
    date_joined             TIMESTAMP WITH TIME ZONE NOT NULL,
    is_deleted              BOOLEAN DEFAULT FALSE,
    address                 BIGINT NOT NULL,
    PRIMARY KEY             (id),
    FOREIGN KEY             (address) REFERENCES addresses(id)
);

CREATE TABLE preferences (
    id                      BIGSERIAL,
    title                   VARCHAR(255) UNIQUE NOT NULL,
    PRIMARY KEY             (id)
);

CREATE TABLE customer_likes (
    preference              BIGINT,
    customer                BIGINT,
    PRIMARY KEY             (preference, customer),
    FOREIGN KEY             (preference) REFERENCES preferences(id),
    FOREIGN KEY             (customer) REFERENCES customers(id)
);

CREATE TABLE voucher_templates (
    id                      BIGSERIAL,
    title                   VARCHAR(255) NOT NULL,
    description             TEXT NOT NULL,
    conditions              TEXT,
    is_published            BOOLEAN DEFAULT TRUE,
    date_created            TIMESTAMP WITH TIME ZONE NOT NULL,
    is_deleted              BOOLEAN DEFAULT FALSE,
    release_date            TIMESTAMP WITH TIME ZONE NOT NULL,
    release_schedule        SCHEDULE_TYPE DEFAULT NULL,
    release_duration        INTERVAL NOT NULL,
    release_size            INTEGER DEFAULT 1,
    last_release            TIMESTAMP WITH TIME ZONE DEFAULT NULL,
    eatery                  BIGINT NOT NULL,
    PRIMARY KEY             (id),
    FOREIGN KEY             (eatery) REFERENCES eateries(id)
);

CREATE TABLE vouchers (
    id                      BIGSERIAL,
    voucher_template        BIGINT NOT NULL,
    release_date            TIMESTAMP WITH TIME ZONE NOT NULL,
    expiry_date             TIMESTAMP WITH TIME ZONE NOT NULL,
    PRIMARY KEY             (id),
    FOREIGN KEY             (voucher_template) REFERENCES voucher_templates(id)
);

CREATE TABLE voucher_instances (
    id                      BIGSERIAL,
    status                  STATUS_TYPE DEFAULT 'unpublished' NOT NULL,
    redemption_code         VARCHAR(20) UNIQUE,
    voucher                 BIGINT NOT NULL,
    customer                BIGINT,
    reviewed                BOOLEAN DEFAULT FALSE,
    PRIMARY KEY             (id),
    FOREIGN KEY             (voucher) REFERENCES vouchers(id),
    FOREIGN KEY             (customer) REFERENCES customers(id)
);

CREATE TABLE favourite_eateries (
    eatery                  BIGINT,
    customer                BIGINT,
    PRIMARY KEY             (eatery, customer),
    FOREIGN KEY             (eatery) REFERENCES eateries(id),
    FOREIGN KEY             (customer) REFERENCES customers(id)
);

CREATE TABLE blocked_eateries (
    eatery                  BIGINT,
    customer                BIGINT,
    PRIMARY KEY             (eatery, customer),
    FOREIGN KEY             (eatery) REFERENCES eateries(id),
    FOREIGN KEY             (customer) REFERENCES customers(id)
);

CREATE TABLE passwords (
    id                      BIGSERIAL,
    password                VARCHAR(255) NOT NULL,
    pass_type               PASS_TYPE DEFAULT 'current' NOT NULL,
    time_created            TIMESTAMP WITH TIME ZONE NOT NULL,
    eatery                  BIGINT,
    customer                BIGINT,
    CONSTRAINT              OneOrOther CHECK (
                                        eatery IS NULL AND customer IS NOT NULL
                                        OR
                                        eatery IS NOT NULL AND customer IS NULL
                                        ),
    PRIMARY KEY             (id),
    FOREIGN KEY             (eatery) REFERENCES eateries(id),
    FOREIGN KEY             (customer) REFERENCES customers(id)
);

CREATE TABLE all_sessions (
    id                      BIGSERIAL,
    refresh_token              VARCHAR(10) NOT NULL,
    time_last_updated       TIMESTAMP WITH TIME ZONE NOT NULL,
    eatery                  BIGINT,
    customer                BIGINT,
    CONSTRAINT              OneOrOther CHECK (
                                        eatery IS NULL AND customer IS NOT NULL
                                        OR
                                        eatery IS NOT NULL AND customer IS NULL
                                        ),
    PRIMARY KEY             (id),
    FOREIGN KEY             (eatery) REFERENCES eateries(id),
    FOREIGN KEY             (customer) REFERENCES customers(id)
);

CREATE TABLE reviews (
    id                      BIGSERIAL,
    description             TEXT NOT NULL,
    rating                  FLOAT NOT NULL,
    date_created            TIMESTAMP WITH TIME ZONE NOT NULL,
    voucher_instance        INTEGER,
    anonymous               BOOLEAN NOT NULL,
    PRIMARY KEY             (id, voucher_instance),
    FOREIGN KEY             (voucher_instance) REFERENCES voucher_instances(id)
);

-- Indexes;

CREATE INDEX vouchers_idx ON voucher_templates(eatery);
CREATE INDEX longitude_idx ON addresses(longitude);
CREATE INDEX latitude_idx ON addresses(latitude);
CREATE UNIQUE INDEX no_hoarding_idx ON voucher_instances (voucher, customer) WHERE customer IS NOT NULL;
