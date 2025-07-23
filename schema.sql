-- USERS TABLE
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    slack_user_id TEXT UNIQUE NOT NULL,
    slack_username TEXT,
    coins INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Automatically update updated_at on UPDATE
CREATE OR REPLACE FUNCTION update_modified_column()
RETURNS TRIGGER AS $$
BEGIN
   NEW.updated_at = NOW();
   RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_users_updated_at
BEFORE UPDATE ON users
FOR EACH ROW
EXECUTE FUNCTION update_modified_column();

-- COIN HISTORY TABLE
CREATE TABLE coin_history (
    id SERIAL PRIMARY KEY,
    giver_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    receiver_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    message TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
