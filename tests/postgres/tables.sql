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
