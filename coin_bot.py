import os
import re
import threading
from flask import Flask
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from dotenv import load_dotenv
from db import add_coin, get_user_coins

# Load environment variables
load_dotenv()

# Initialize Slack app
app = App(token=os.environ["SLACK_BOT_TOKEN"])

# Handle messages with ++ or thank
@app.event("message")
def handle_message(event, say):
    text = event.get("text", "")
    sender = event.get("user", "")

    if sender is None or event.get("subtype") is not None:
        return

    mentions = re.findall(r"<@(\w+)>", text)

    for user_id in mentions:
        if user_id != sender and re.search(r"\b\+\+|\bthank", text.lower()):
            add_coin(sender, user_id, message=text)
            total = get_user_coins(user_id)
            say(
                text=f"<@{user_id}> now has {total} coin(s)! 🎉",
                thread_ts=event["ts"]
            )

# Dummy Flask app to bind a port (required for Web Service)
flask_app = Flask(__name__)

@flask_app.route("/")
def health_check():
    return "Coin bot is running!", 200

# Start Slack bot in separate thread
def run_bot():
    print("✅ Coin Bot is connected and listening via Socket Mode!")
    handler = SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    handler.start()

if __name__ == "__main__":
    threading.Thread(target=run_bot).start()
    flask_app.run(host="0.0.0.0", port=10000)
