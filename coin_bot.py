import os
import re
import threading
from flask import Flask
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from dotenv import load_dotenv
from db import add_coin, get_user_coins
from slack_sdk.errors import SlackApiError

load_dotenv()

app = App(token=os.environ["SLACK_BOT_TOKEN"])

@app.event("message")
def handle_message(event, say, client):
    print("Handling message started.")
    text = event.get("text", "")
    sender = event.get("user", "")

    if sender is None or event.get("subtype") is not None:
       print("Sender is none") 
       return

    mentions = re.findall(r"<@(\w+)>", text)
    sender_name = get_username_by_id(client, sender)

    print("sender name: {sender_name}")

    for user_id in mentions:
        if user_id != sender and ("++" in text or "thank" in text.lower()):
            print("sender is not the receiver and a coin was given")
            receiver_name = get_username_by_id(client, user_id)

            add_coin(sender, sender_name, user_id, receiver_name, message=text)
            total = get_user_coins(user_id)
            
            say(
                text=f"<@{user_id}> now has {total} coin(s)! 🎉",
                thread_ts=event["ts"]
            )
            print("All done!") 

flask_app = Flask(__name__)

@flask_app.route("/")
def health_check():
    return "Coin bot is running!", 200

def get_username_by_id(client, user_id):
    try:
        user_info = client.users_info(user=user_id)
        return user_info["user"]["name"]
    except SlackApiError:
        return user_id  # fallback

# Start Slack bot in separate thread
def run_bot():
    print("✅ Coin Bot is connected and listening via Socket Mode!")
    handler = SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    handler.start()

if __name__ == "__main__":
    threading.Thread(target=run_bot).start()

    # Start dummy Flask server to bind to the port Render expects
    flask_app.run(host="0.0.0.0", port=10000)
