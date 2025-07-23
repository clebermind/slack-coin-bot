import os
import re
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from dotenv import load_dotenv
from db import add_coin, get_or_create_user, get_user_coins

load_dotenv()

app = App(token=os.environ["SLACK_BOT_TOKEN"])

@app.event("message")
def handle_message(event, say):
    text = event.get("text", "")
    sender = event.get("user", "")

    # Ignore bot messages and edited messages
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

if __name__ == "__main__":
    handler = SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    handler.start()
