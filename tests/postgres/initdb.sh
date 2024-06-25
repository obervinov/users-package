#!/bin/bash
set -e

echo "host postgres postgres 0.0.0.0/0 trust" >> "$PGDATA/pg_hba.conf"

# Schema for the users table #
psql -v ON_ERROR_STOP=1 --username postgres --dbname postgres <<-EOSQL
	CREATE TABLE users (
		id serial PRIMARY KEY,
		user_id VARCHAR (50) UNIQUE NOT NULL,
		chat_id VARCHAR (50) NOT NULL,
		status VARCHAR (50) NOT NULL DEFAULT 'denied',
	);
EOSQL

psql -v ON_ERROR_STOP=1 --username postgres --dbname postgres <<-EOSQL
	CREATE TABLE users_requests (
		id serial PRIMARY KEY,
		user_id VARCHAR (50) UNIQUE NOT NULL,
		message_id VARCHAR (50),
		chat_id VARCHAR (50),
		authentication VARCHAR (50) NOT NULL,
		authorization VARCHAR (255) NOT NULL,
		timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
		rate_limits TIMESTAMP,
	);
EOSQL
