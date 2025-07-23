# 🪙 Slack Coin Bot

A simple and fun Slack bot that lets users give each other "coins" by typing `++` or `thanks` when mentioning someone — like this:

```plaintext
@cleber.mendes++
```

The bot tracks coin totals, logs transactions in a PostgreSQL database, and replies in the thread with the updated balance:

```plaintext
@cleber.mendes now has 5 coin(s)! 🎉
```

## 🚀 Features

- ✅ Track how many coins each user receives
- ✅ Log every transaction with giver, receiver, and message
- ✅ Reply in the same thread where coin was given
- ✅ Ignore bots, self-giving, and edited messages
- ✅ Built in Python using Slack Bolt
- ✅ Hosted for free on [Render](https://render.com)
- ✅ PostgreSQL database for persistence

---

## 🛠️ Tech Stack

- Python 3
- [Slack Bolt SDK](https://slack.dev/bolt-python/)
- PostgreSQL (Render Free Tier)
- Hosted as a background worker on Render

---

## 📂 Project Structure

```plaintext
.
├── coin_bot.py        # Main bot logic (Slack event handler)
├── db.py              # Database connection and queries
├── requirements.txt   # Python dependencies
├── render.yaml        # Render deployment config
├── .env.example       # Environment variable template
└── schema.sql         # PostgreSQL table and trigger definitions
```

---

## ⚙️ Setup & Deployment

### 1. Create the PostgreSQL Database

- Go to [Render > New PostgreSQL](https://dashboard.render.com/)
- Copy the `DATABASE_URL`

---

### 2. Create a Slack App

- Go to [Slack API Dashboard](https://api.slack.com/apps)
- Create a new app and enable:
  - **Socket Mode**
  - **Event Subscriptions**
    - Subscribe to `message.channels`
- Add OAuth scopes:
  - `app_mentions:read`
  - `chat:write`
  - `channels:history`
- Install the bot to your workspace

---

### 3. Set Up Environment Variables

Create a `.env` file locally (or set them in Render):

SLACK_BOT_TOKEN=your-xoxb-token
SLACK_APP_TOKEN=your-xapp-token
DATABASE_URL=your-postgresql-connection-string

---

### 4. Deploy to Render

- Push your code to GitHub
- Go to Render > **New Web Service**
  - Type: **Background Worker**
  - Runtime: **Python**
  - Start command: `python coin_bot.py`
- Connect to your GitHub repo
- Add environment variables in the Render dashboard

---

## 🧪 Usage

In Slack, type:

@username ++
@username thanks!

The bot will:
- Log the transaction
- Update the coin count
- Reply in the same thread

---

## 🗃 Database Schema

### 🛠️ Database Setup

Before running the bot, you need to create the required tables in your PostgreSQL database.

You can do this by running the [`schema.sql`](./schema.sql) script:

```bash
psql "your_connection_string" < schema.sql 
```

---

### `users` table

| Column           | Type      |
|------------------|-----------|
| id               | SERIAL PK |
| slack_user_id    | TEXT UNIQUE |
| slack_username   | TEXT      |
| coins            | INTEGER   |
| created_at       | TIMESTAMP |
| updated_at       | TIMESTAMP |

### `coin_history` table

| Column           | Type      |
|------------------|-----------|
| id               | SERIAL PK |
| giver_id         | FK → users |
| receiver_id      | FK → users |
| message          | TEXT      |
| created_at       | TIMESTAMP |

---

## 📌 Example Message Flow

User: @cleber.mendes ++
Bot: (in thread) @cleber.mendes now has 4 coin(s)! 🎉

---

## 🧩 Ideas for Next Features

- `/coins` slash command to check your balance
- `/leaderboard` to see top coin holders
- Emoji reactions as coin triggers

---

## 🧑‍💻 Maintainer

Made by [Cleber Mendes](https://github.com/clebermind)  
Feel free to fork, improve, and share!

---

## 🪙 License

This project is licensed under the [GNU General Public License v3.0 (GPL-3.0)](https://www.gnu.org/licenses/gpl-3.0.html).

You are free to use, modify, and distribute this software under the terms of the GPL-3.0 license. Any derivative works must also be distributed under the same license.
