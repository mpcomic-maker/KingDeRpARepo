import tweepy
import feedparser
import random
import time
import requests
import schedule
import threading

# === YOUR KEYS (@KingDeRpA) ===
API_KEY = "j06H2aXequmKlq3ynI6mKQMJW"
API_SECRET = "VswGI4agj6rbFl0K0UGryRYXqvf6nV1Vj9RyVOIDzHiPZPW5qX"
ACCESS_TOKEN = "508149399-z1fNz2rLHk6FqrBtYpfEvsIpJWIinRMamtyGWEv7"
ACCESS_TOKEN_SECRET = "6I3V9h2SniGkEDdv6Qr3uHEVmBAniQ58lVtnUSIHrZSS6"
BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAADS25QEAAAAAndlkiBIF3MZQjWPt%2FBpee9L%2F6ts%3D3m13garC7UigPaDXtUOlb6n0B66uUNArqUeEQCZA59X25TOzHk"

# === GROK API KEY ===
GROK_API_KEY = "PASTE_YOUR_GROK_API_KEY_HERE"

# === AUTH ===
client = tweepy.Client(
    consumer_key=API_KEY,
    consumer_secret=API_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_TOKEN_SECRET,
    bearer_token=BEARER_TOKEN,
    wait_on_rate_limit=True
)

# === RSS FEEDS ===
FEEDS = [
    "https://www.thegatewaypundit.com/feed/",
    "https://feeds.feedburner.com/breitbart",
    "https://www.newsmax.com/rss/",
    "https://www.dailywire.com/feeds/rss",
    "https://www.zerohedge.com/rss"
]

# === GET ARTICLE ===
def get_article():
    feed = feedparser.parse(random.choice(FEEDS))
    if not feed.entries: return get_article()
    a = random.choice(feed.entries[:3])
    title = a.title[:80] + "..." if len(a.title) > 80 else a.title
    return f"{title}\n\n{a.link}"

# === POST NEWS ===
def post_news():
    tweet = f"🚨 BREAKING 🚨\n\n{get_article()}\n\nComment below."
    try:
        r = client.create_tweet(text=tweet)
        print(f"POSTED: https://x.com/KingDeRpA/status/{r.data['id']}")
    except Exception as e:
        print("ERROR:", e)

# === GROK REPLY ===
def grok_reply(user_text):
    url = "https://api.x.ai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROK_API_KEY}", "Content-Type": "application/json"}
    data = {
        "model": "grok-beta",
        "messages": [
            {"role": "system", "content": "You are @KingDeRpA: a satirical, Florida-style bot. Use humor, zingers, hypocrisy traps. Keep replies <200 chars. End with a question. Emojis: 🐸🌴"},
            {"role": "user", "content": user_text}
        ],
        "max_tokens": 80,
        "temperature": 0.9
    }
    try:
        resp = requests.post(url, json=data, headers=headers).json()
        return resp['choices'][0]['message']['content'].strip()
    except:
        return "🤖 Beep boop. Florida man confused. Thoughts? 🐊"

# === CHECK @MENTIONS ===
def check_mentions():
    try:
        mentions = client.get_users_mentions(client.get_me().data.id, max_results=5)
        if not mentions.data: return
        for m in mentions.data:
            if m.in_reply_to_tweet_id: continue
            reply = grok_reply(m.text)
            client.create_tweet(text=f"@{m.author_id} {reply}", in_reply_to_tweet_id=m.id)
            print(f"REPLIED to {m.id}")
    except Exception as e:
        print("MENTION ERROR:", e)

# === AUTO-RUN ===
def run_bot():
    post_news()
    check_mentions()

# === SCHEDULE ===
schedule.every(6).hours.do(post_news)
schedule.every(30).minutes.do(check_mentions)

# === START ===
run_bot()
threading.Thread(target=lambda: [schedule.run_pending(), time.sleep(60)], daemon=True).start()
print("KingDeRpA BOT RUNNING 24/7 on Render | News every 6h | Replies every 30m")

# Infinite loop for Render
while True:
    time.sleep(1)