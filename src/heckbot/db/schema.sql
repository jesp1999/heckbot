-- Sqlite3 schema for the bot
CREATE TABLE IF NOT EXISTS tasks (
    completed BOOLEAN,
    task TEXT,
    message_id INT,
    channel_id INT,
    end_time TEXT
);