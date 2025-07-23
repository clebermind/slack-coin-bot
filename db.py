import os
import psycopg2

conn = psycopg2.connect(os.environ["DATABASE_URL"])
conn.autocommit = True

def get_or_create_user(slack_user_id, slack_username):
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO users (slack_user_id, slack_username)
            VALUES (%s, %s)
            ON CONFLICT (slack_user_id) DO NOTHING
        """, (slack_user_id, slack_username))

        cur.execute("""
            SELECT id, coins FROM users WHERE slack_user_id = %s
        """, (slack_user_id,))
        return cur.fetchone()

def add_coin(giver_id, receiver_id, message=""):
    giver = get_or_create_user(giver_id)
    receiver = get_or_create_user(receiver_id)

    if not giver or not receiver:
        raise ValueError("Unable to find or create user(s).")

    # result[0] is id
    giver_db_id = giver[0]
    receiver_db_id = receiver[0]

    with conn.cursor() as cur:
        cur.execute("""
            UPDATE users SET coins = coins + 1 WHERE id = %s
        """, (receiver_db_id,))

        cur.execute("""
            INSERT INTO coin_history (giver_id, receiver_id, message)
            VALUES (%s, %s, %s)
        """, (giver_db_id, receiver_db_id, message))

def get_user_coins(slack_user_id):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT coins FROM users WHERE slack_user_id = %s
        """, (slack_user_id,))
        result = cur.fetchone()
        return result[0] if result else 0