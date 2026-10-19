import os, hmac, hashlib, json, sqlite3, threading, time, uuid
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import requests
from flask import Flask, request, abort

# ---------- Settings (set these in your host's Variables) ----------
BOT_TOKEN = os.environ["BOT_TOKEN"]
PAYSTACK_SECRET = os.environ["PAYSTACK_SECRET_KEY"]
GROUP_ID = os.environ.get("GROUP_ID", "")
CHANNEL_ID = os.environ.get("CHANNEL_ID", "")
PUBLIC_URL = os.environ.get("PUBLIC_URL", "").rstrip("/")
TG_SECRET = os.environ.get("TG_WEBHOOK_SECRET", "change-me")
ADMIN_IDS = {int(x) for x in os.environ.get("ADMIN_IDS", "").replace(" ", "").split(",") if x}
GRACE_DAYS = int(os.environ.get("GRACE_DAYS", "5"))
PRICE_NAIRA = int(os.environ.get("PRICE_NAIRA", "2000"))
PLAN_DAYS = int(os.environ.get("PLAN_DAYS", "30"))
DB_PATH = os.environ.get("DB_PATH", "/data/subs.db")
TZ = ZoneInfo("Africa/Lagos")
AMOUNT_KOBO = PRICE_NAIRA * 100

TG = f"https://api.telegram.org/bot{BOT_TOKEN}"
PS = "https://api.paystack.co"
app = Flask(__name__)
lock = threading.Lock()

try:
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
except Exception:
    DB_PATH = "subs.db"


# ---------- Database ----------
def db(sql, args=(), fetch=None):
    with lock:
        con = sqlite3.connect(DB_PATH)
        con.row_factory = sqlite3.Row
        try:
            cur = con.execute(sql, args)
            out = cur.fetchall() if fetch == "all" else cur.fetchone() if fetch == "one" else cur.rowcount
            con.commit()
            return out
        finally:
            con.close()


db("CREATE TABLE IF NOT EXISTS subs (tg_id INTEGER PRIMARY KEY, email TEXT, expiry TEXT, last_reminded TEXT, removed INTEGER DEFAULT 0)")
db("CREATE TABLE IF NOT EXISTS refs (ref TEXT PRIMARY KEY, tg_id INTEGER, email TEXT, processed INTEGER DEFAULT 0, created TEXT)")
db("CREATE TABLE IF NOT EXISTS meta (k TEXT PRIMARY KEY, v TEXT)")


# ---------- Telegram helpers ----------
def tg(method, **params):
    try:
        return requests.post(f"{TG}/{method}", json=params, timeout=20).json()
    except Exception as e:
        print("TG error", method, e)
        return {"ok": False}


def send(chat_id, text):
    tg("sendMessage", chat_id=chat_id, text=text)


def today():
    return datetime.now(TZ).date()


def invite_links():
    links = []
    for name, chat in (("Group", GROUP_ID), ("Channel", CHANNEL_ID)):
        if not chat:
            continue
        r = tg("createChatInviteLink", chat_id=int(chat), member_limit=1,
               expire_date=int(time.time()) + 86400)
        if r.get("ok"):
            links.append(f"{name}: {r['result']['invite_link']}")
    return links


def grant(tg_id, days, email=None):
    row = db("SELECT * FROM subs WHERE tg_id=?", (tg_id,), "one")
    base = today()
    if row and row["removed"] == 0:
        old = datetime.strptime(row["expiry"], "%Y-%m-%d").date()
        if old > base:
            base = old
    new_exp = (base + timedelta(days=days)).isoformat()
    db("INSERT INTO subs (tg_id,email,expiry,last_reminded,removed) VALUES (?,?,?,NULL,0) "
       "ON CONFLICT(tg_id) DO UPDATE SET expiry=?, last_reminded=NULL, removed=0, "
       "email=COALESCE(?, email)", (tg_id, email, new_exp, new_exp, email))
    links = invite_links()
    msg = f"Access active until {new_exp}.\n\nYour one-time join links (valid 24 hours):\n" + "\n".join(links)
    send(tg_id, msg)
    return new_exp


def remove_member(tg_id):
    for chat in (GROUP_ID, CHANNEL_ID):
        if chat:
            tg("banChatMember", chat_id=int(chat), user_id=tg_id)
            tg("unbanChatMember", chat_id=int(chat), user_id=tg_id, only_if_banned=True)


# ---------- Paystack ----------
def paystack_headers():
    return {"Authorization": f"Bearer {PAYSTACK_SECRET}"}


def start_payment(tg_id, email):
    ref = "sub_" + uuid.uuid4().hex[:18]
    r = requests.post(f"{PS}/transaction/initialize", headers=paystack_headers(), timeout=20, json={
        "email": email, "amount": AMOUNT_KOBO, "currency": "NGN", "reference": ref,
        "metadata": {"telegram_id": tg_id}}).json()
    if not r.get("status"):
        return None
    db("INSERT INTO refs (ref,tg_id,email,created) VALUES (?,?,?,?)",
       (ref, tg_id, email, datetime.now(TZ).isoformat()))
    return r["data"]["authorization_url"]


@app.route("/paystack", methods=["POST"])
def paystack_webhook():
    raw = request.get_data()
    sig = request.headers.get("x-paystack-signature", "")
    expected = hmac.new(PAYSTACK_SECRET.encode(), raw, hashlib.sha512).hexdigest()
    if not hmac.compare_digest(sig, expected):
        abort(401)
    event = json.loads(raw)
    if event.get("event") != "charge.success":
        return "ok", 200
    ref = event.get("data", {}).get("reference", "")
    row = db("SELECT * FROM refs WHERE ref=?", (ref,), "one")
    if not row or row["processed"]:
        return "ok", 200  # unknown or duplicate reference
    v = requests.get(f"{PS}/transaction/verify/{ref}", headers=paystack_headers(), timeout=20).json()
    d = v.get("data", {}) if v.get("status") else {}
    if d.get("status") != "success" or d.get("amount") != AMOUNT_KOBO or d.get("currency") != "NGN":
        return "ok", 200
    if db("UPDATE refs SET processed=1 WHERE ref=? AND processed=0", (ref,)) == 1:
        grant(row["tg_id"], PLAN_DAYS, row["email"])
    return "ok", 200


# ---------- Telegram webhook ----------
@app.route("/telegram", methods=["POST"])
def telegram_webhook():
    if request.headers.get("X-Telegram-Bot-Api-Secret-Token") != TG_SECRET:
        abort(401)
    msg = (request.get_json(silent=True) or {}).get("message")
    if not msg or msg.get("chat", {}).get("type") != "private":
        return "ok", 200
    uid, text = msg["from"]["id"], (msg.get("text") or "").strip()
    cmd, *rest = text.split()
    cmd = cmd.split("@")[0].lower()

    if cmd == "/start":
        send(uid, f"Welcome! Subscription: N{PRICE_NAIRA} for {PLAN_DAYS} days.\n\n"
                  "To pay, send:\n/pay youremail@example.com\n\nCheck your plan: /status")
    elif cmd == "/pay":
        email = rest[0] if rest else ""
        if "@" not in email or "." not in email:
            send(uid, "Please include your email, e.g.\n/pay youremail@example.com")
        else:
            url = start_payment(uid, email)
            send(uid, f"Pay N{PRICE_NAIRA} here:\n{url}\n\nAccess is added automatically after payment is confirmed."
                 if url else "Could not create a payment link. Please try again.")
    elif cmd == "/status":
        row = db("SELECT * FROM subs WHERE tg_id=?", (uid,), "one")
        send(uid, f"Active until {row['expiry']}." if row and not row["removed"]
             else "No active subscription. Send /pay youremail@example.com")
    elif cmd == "/grant" and uid in ADMIN_IDS:
        try:
            target, days = int(rest[0]), int(rest[1]) if len(rest) > 1 else PLAN_DAYS
            send(uid, f"Done. {target} active until {grant(target, days)}")
        except Exception:
            send(uid, "Use: /grant TELEGRAM_ID 30")
    return "ok", 200


@app.route("/")
def home():
    return "Bot is running", 200


# ---------- Daily reminders and removals ----------
def daily_job():
    t = today()
    for row in db("SELECT * FROM subs WHERE removed=0", (), "all"):
        d = (datetime.strptime(row["expiry"], "%Y-%m-%d").date() - t).days
        uid = row["tg_id"]
        if d < -GRACE_DAYS:
            remove_member(uid)
            db("UPDATE subs SET removed=1 WHERE tg_id=?", (uid,))
            send(uid, "Your subscription has ended and you were removed. Send /pay youremail@example.com to rejoin.")
        elif d <= 5 and row["last_reminded"] != t.isoformat():
            if d > 0:
                text = f"Reminder: your subscription expires in {d} day(s)."
            elif d == 0:
                text = "Your subscription expires today."
            else:
                text = f"Your subscription expired {-d} day(s) ago. You will be removed in {GRACE_DAYS + d + 1} day(s)."
            send(uid, text + f"\nRenew: /pay youremail@example.com (N{PRICE_NAIRA})")
            db("UPDATE subs SET last_reminded=? WHERE tg_id=?", (t.isoformat(), uid))


def scheduler():
    while True:
        try:
            now = datetime.now(TZ)
            last = db("SELECT v FROM meta WHERE k='last_run'", (), "one")
            if now.hour >= 8 and (not last or last["v"] != now.date().isoformat()):
                daily_job()
                db("INSERT INTO meta (k,v) VALUES ('last_run',?) ON CONFLICT(k) DO UPDATE SET v=?",
                   (now.date().isoformat(),) * 2)
        except Exception as e:
            print("Scheduler error", e)
        time.sleep(600)


def setup():
    if PUBLIC_URL:
        tg("setWebhook", url=f"{PUBLIC_URL}/telegram", secret_token=TG_SECRET,
           allowed_updates=["message"])
    threading.Thread(target=scheduler, daemon=True).start()


setup()
