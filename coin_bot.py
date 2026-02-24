import os
import re
import threading
import logging
import sys
from flask import Flask
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from dotenv import load_dotenv
from db import add_coin, get_user_coins
from slack_sdk.errors import SlackApiError

# Configure logging to stdout (important for Render)
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Force stdout to be unbuffered for immediate log visibility on Render
sys.stdout.reconfigure(line_buffering=True)

load_dotenv()

logger.info("Starting Coin Bot...")
logger.info(f"SLACK_BOT_TOKEN present: {bool(os.environ.get('SLACK_BOT_TOKEN'))}")
logger.info(f"SLACK_APP_TOKEN present: {bool(os.environ.get('SLACK_APP_TOKEN'))}")

app = App(
    token=os.environ["SLACK_BOT_TOKEN"],
    logger=logger
)

# Middleware to log ALL incoming requests for debugging
@app.middleware
def log_all_requests(body, next, logger):
    event = body.get("event", {})
    logger.info(f"[MIDDLEWARE] Incoming request - type: {body.get('type')} | event_type: {event.get('type')} | subtype: {event.get('subtype')}")
    return next()

@app.event("message")
def handle_message(event, say, client):
    logger.info(f"Handling message event: {event}")
    text = event.get("text", "")
    sender = event.get("user", "")

    if sender is None or event.get("subtype") is not None:
       logger.info(f"Ignoring message - sender: {sender}, subtype: {event.get('subtype')}") 
       return

    mentions = re.findall(r"<@(\w+)>", text)
    sender_name = get_username_by_id(client, sender)

    logger.info(f"Message from {sender_name}: '{text}' - mentions: {mentions}")

    for user_id in mentions:
        if user_id != sender and ("++" in text or "thank" in text.lower()):
            logger.info(f"Coin triggered! Sender {sender} -> Receiver {user_id}")
            receiver_name = get_username_by_id(client, user_id)

            add_coin(sender, sender_name, user_id, receiver_name, message=text)
            total = get_user_coins(user_id)
            
            say(
                text=f"<@{user_id}> now has {total} coin(s)! 🎉",
                thread_ts=event["ts"]
            )
            logger.info(f"Coin given! {receiver_name} now has {total} coins") 

flask_app = Flask(__name__)

@flask_app.route("/")
def health_check():
    logger.info("Health check endpoint called")
    return "Coin bot is running!", 200

def get_username_by_id(client, user_id):
    try:
        user_info = client.users_info(user=user_id)
        return user_info["user"]["name"]
    except SlackApiError as e:
        logger.error(f"Failed to get username for {user_id}: {e}")
        return user_id  # fallback

# Start Slack bot in separate thread
def run_bot():
    try:
        logger.info("Attempting to start Socket Mode handler...")
        handler = SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
        logger.info("✅ Coin Bot is connected and listening via Socket Mode!")
        handler.start()
    except Exception as e:
        logger.error(f"❌ Failed to start Socket Mode handler: {e}")
        raise

if __name__ == "__main__":
    logger.info("=== Coin Bot Starting ===")
    
    # Start bot in a daemon thread so it exits when main thread exits
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    
    logger.info("Starting Flask health check server on port 10000...")
    # Start Flask server to keep Render happy
    flask_app.run(host="0.0.0.0", port=10000)

