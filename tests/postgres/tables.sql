-- Schema for the users table
CREATE TABLE users (
    id serial PRIMARY KEY,
    user_id VARCHAR (50) UNIQUE NOT NULL,
    chat_id VARCHAR (50) NOT NULL,
    status VARCHAR (50) NOT NULL DEFAULT 'denied'
);

-- Schema for the users_requests table
CREATE TABLE users_requests (
    id serial PRIMARY KEY,
    user_id VARCHAR (50) NOT NULL,
    message_id VARCHAR (50),
    chat_id VARCHAR (50),
    authentication VARCHAR (50) NOT NULL,
    "authorization" VARCHAR (255) NOT NULL,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    rate_limits TIMESTAMP
);

-- Schema for the users_tokens table
CREATE TABLE users_tokens (
    id serial PRIMARY KEY,
    user_id VARCHAR (255) NOT NULL,
    token_hash VARCHAR (128) NOT NULL,
    token_salt VARCHAR (64) NOT NULL,
    token_expires_at TIMESTAMP NOT NULL,
    token_used BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_users_tokens_user_id ON users_tokens(user_id);
