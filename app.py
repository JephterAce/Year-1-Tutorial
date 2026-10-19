"""Telegram subscription bot with verified Paystack payments.

Students: pay, status, join links, receipts, help, self-service payment check.
Admin: stats, members, expiring, find, grant, revoke, broadcast, export, backup.
Safety: signature-checked webhooks, double verification, duplicate protection,
self-healing reconcile, abandoned-checkout nudges, optional gatekeeper.
"""
import os, io, csv, html, hmac, hashlib, json, sqlite3, threading, time, uuid, traceback
from collections import deque
from datetime import datetime, timedelta, timezone

import requests
from flask import Flask, request, abort, jsonify

try:
    from zoneinfo import ZoneInfo
    TZ = ZoneInfo("Africa/Lagos")
except Exception:
    TZ = timezone(timedelta(hours=1))

# ======================= Settings (Railway Variables) =======================
BOT_TOKEN = os.environ["BOT_TOKEN"]
PAYSTACK_SECRET = os.environ["PAYSTACK_SECRET_KEY"]
GROUP_ID = os.environ.get("GROUP_ID", "").strip()
CHANNEL_ID = os.environ.get("CHANNEL_ID", "").strip()
PUBLIC_URL = os.environ.get("PUBLIC_URL", "").rstrip("/")
TG_SECRET = os.environ.get("TG_WEBHOOK_SECRET", "change-me")
ADMIN_IDS = {int(x) for x in os.environ.get("ADMIN_IDS", "").replace(" ", "").split(",") if x}
GRACE_DAYS = int(os.environ.get("GRACE_DAYS", "5"))
REMIND_DAYS = int(os.environ.get("REMIND_DAYS", "5"))
PRICE_NAIRA = int(os.environ.get("PRICE_NAIRA", "2000"))
PLAN_DAYS = int(os.environ.get("PLAN_DAYS", "30"))
BUSINESS = os.environ.get("BUSINESS_NAME", "Year 1 Tutorials")
SUPPORT = os.environ.get("SUPPORT_CONTACT", "@JephterEmmanuel").strip()
if SUPPORT.startswith("t.me/"):
    SUPPORT = "https://" + SUPPORT
SUPPORT_URL = ("https://t.me/" + SUPPORT[1:]) if SUPPORT.startswith("@") else (SUPPORT if SUPPORT.startswith("http") else "")
GATEKEEPER = os.environ.get("GATEKEEPER", "off").strip().lower() == "on"
SUMMARY_HOUR = int(os.environ.get("SUMMARY_HOUR", "8"))
DB_PATH = os.environ.get("DB_PATH", "/data/subs.db")
AMOUNT_KOBO = PRICE_NAIRA * 100

TG = f"https://api.telegram.org/bot{BOT_TOKEN}"
PS = "https://api.paystack.co"
BOT_USERNAME = ""
app = Flask(__name__)
lock = threading.Lock()

try:
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
except Exception:
    DB_PATH = "subs.db"


# ============================== Database ==============================
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


for _ddl in (
    "CREATE TABLE IF NOT EXISTS subs (tg_id INTEGER PRIMARY KEY, email TEXT, expiry TEXT, last_reminded TEXT, removed INTEGER DEFAULT 0)",
    "CREATE TABLE IF NOT EXISTS refs (ref TEXT PRIMARY KEY, tg_id INTEGER, email TEXT, processed INTEGER DEFAULT 0, created TEXT, nudged INTEGER DEFAULT 0)",
    "CREATE TABLE IF NOT EXISTS meta (k TEXT PRIMARY KEY, v TEXT)",
    "CREATE TABLE IF NOT EXISTS emails (tg_id INTEGER PRIMARY KEY, email TEXT)",
    "CREATE TABLE IF NOT EXISTS users (tg_id INTEGER PRIMARY KEY, first_name TEXT, username TEXT, joined TEXT, blocked INTEGER DEFAULT 0)",
    "CREATE TABLE IF NOT EXISTS payments (ref TEXT PRIMARY KEY, tg_id INTEGER, email TEXT, amount INTEGER, channel TEXT, paid_at TEXT)",
):
    db(_ddl)
try:
    db("ALTER TABLE refs ADD COLUMN nudged INTEGER DEFAULT 0")
except sqlite3.OperationalError:
    pass


# ============================== Helpers ==============================
def now():
    return datetime.now(TZ)


def today():
    return now().date()


def esc(x):
    return html.escape(str(x or ""))


def naira(n):
    return f"\u20a6{int(n):,}"


def fdate(d):
    return d.strftime("%d %b %Y")


def parse_date(s):
    return datetime.strptime(s, "%Y-%m-%d").date()


def bar(d):
    n = max(0, min(10, round(10 * d / PLAN_DAYS)))
    return "\u25b0" * n + "\u25b1" * (10 - n)


def valid_email(e):
    return bool(e) and " " not in e and e.count("@") == 1 and "." in e.split("@")[-1] and len(e) < 120


def tg(method, **params):
    try:
        r = requests.post(f"{TG}/{method}", json=params, timeout=20).json()
        if not r.get("ok"):
            print("TG not ok:", method, r.get("error_code"), r.get("description"))
        return r
    except Exception as e:
        print("TG error", method, e)
        return {"ok": False}


def send(chat_id, text, markup=None, html_mode=True):
    p = {"chat_id": chat_id, "text": text, "disable_web_page_preview": True}
    if html_mode:
        p["parse_mode"] = "HTML"
    if markup:
        p["reply_markup"] = markup
    r = tg("sendMessage", **p)
    if not r.get("ok") and r.get("error_code") == 403:
        db("UPDATE users SET blocked=1 WHERE tg_id=?", (chat_id,))
    return bool(r.get("ok"))


def send_document(chat_id, filename, data, caption=""):
    try:
        requests.post(f"{TG}/sendDocument", data={"chat_id": chat_id, "caption": caption},
                      files={"document": (filename, data)}, timeout=60)
    except Exception as e:
        print("sendDocument error", e)


def alert_admins(text):
    for a in ADMIN_IDS:
        send(a, text)


_last_err = {}


def err_alert(where):
    tb = traceback.format_exc()
    print(tb)
    key = tb.strip().splitlines()[-1][:120]
    if time.time() - _last_err.get(key, 0) > 1800:
        _last_err[key] = time.time()
        alert_admins(f"\u26a0\ufe0f <b>Bot error</b> in {esc(where)}:\n<code>{esc(key)}</code>")


def record_user(frm):
    db("INSERT INTO users (tg_id, first_name, username, joined, blocked) VALUES (?,?,?,?,0) "
       "ON CONFLICT(tg_id) DO UPDATE SET first_name=excluded.first_name, username=excluded.username, blocked=0",
       (frm["id"], frm.get("first_name", ""), (frm.get("username") or "").lower(), now().isoformat()))


def first_name(uid):
    r = db("SELECT first_name FROM users WHERE tg_id=?", (uid,), "one")
    return (r["first_name"] if r and r["first_name"] else "there")


def label(uid):
    r = db("SELECT first_name, username FROM users WHERE tg_id=?", (uid,), "one")
    if not r:
        return str(uid)
    name = esc(r["first_name"] or "Student")
    return f"{name} (@{esc(r['username'])})" if r["username"] else name


def get_email(uid):
    r = db("SELECT email FROM emails WHERE tg_id=?", (uid,), "one")
    return r["email"] if r else None


def save_email(uid, email):
    db("INSERT INTO emails (tg_id,email) VALUES (?,?) ON CONFLICT(tg_id) DO UPDATE SET email=?", (uid, email, email))


def get_sub(uid):
    return db("SELECT * FROM subs WHERE tg_id=?", (uid,), "one")


# ============================ Access control ============================
def invite_links():
    out, errs = [], []
    for text, chat in (("\U0001F465 Join the group", GROUP_ID), ("\U0001F4DA Join the materials channel", CHANNEL_ID)):
        if not chat:
            continue
        r = tg("createChatInviteLink", chat_id=int(chat), member_limit=1, expire_date=int(time.time()) + 86400)
        if r.get("ok"):
            out.append((text, r["result"]["invite_link"]))
        else:
            errs.append(f"{text}: {r.get('description')}")
    return out, errs


def grant(tg_id, days, email=None):
    row = get_sub(tg_id)
    base = today()
    if row and row["removed"] == 0:
        old = parse_date(row["expiry"])
        if old > base:
            base = old
    new_exp = base + timedelta(days=days)
    iso = new_exp.isoformat()
    db("INSERT INTO subs (tg_id,email,expiry,last_reminded,removed) VALUES (?,?,?,NULL,0) "
       "ON CONFLICT(tg_id) DO UPDATE SET expiry=?, last_reminded=NULL, removed=0, email=COALESCE(?, email)",
       (tg_id, email, iso, iso, email))
    return new_exp


def send_access(uid, headline):
    links, errs = invite_links()
    if links:
        markup = {"inline_keyboard": [[{"text": t, "url": u}] for t, u in links]}
        return send(uid, headline + "\n\nTap below to join. Each link works <b>once</b> and expires in 24 hours. "
                                    "Lost it? Tap \U0001F517 My links.", markup)
    alert_admins(f"\u26a0\ufe0f Could not create join links for {label(uid)} (<code>{uid}</code>): "
                 f"{esc('; '.join(errs) or 'no chat configured')}. Check the bot is an admin in the group and "
                 "channel with the 'Invite users' permission.")
    return send(uid, headline + "\n\nI could not create your join links just now. The admin has been alerted "
                                "and will add you shortly.")


def remove_from(chat, uid):
    if chat:
        tg("banChatMember", chat_id=int(chat), user_id=uid)
        tg("unbanChatMember", chat_id=int(chat), user_id=uid, only_if_banned=True)


def remove_member(uid):
    remove_from(GROUP_ID, uid)
    remove_from(CHANNEL_ID, uid)


# =============================== Payments ===============================
def ps_headers():
    return {"Authorization": f"Bearer {PAYSTACK_SECRET}"}


def start_payment(tg_id, email):
    ref = "sub_" + uuid.uuid4().hex[:18]
    body = {"email": email, "amount": AMOUNT_KOBO, "currency": "NGN", "reference": ref,
            "metadata": {"telegram_id": tg_id}}
    if BOT_USERNAME:
        body["callback_url"] = f"https://t.me/{BOT_USERNAME}"
    try:
        r = requests.post(f"{PS}/transaction/initialize", headers=ps_headers(), json=body, timeout=20).json()
    except Exception as e:
        print("initialize error", e)
        return None
    if not r.get("status"):
        print("initialize failed", r)
        return None
    db("INSERT INTO refs (ref,tg_id,email,created) VALUES (?,?,?,?)", (ref, tg_id, email, now().isoformat()))
    return r["data"]["authorization_url"]


def process_payment(ref):
    """Verify with Paystack and grant access. Returns ok / unknown / duplicate / unpaid / mismatch / error."""
    row = db("SELECT * FROM refs WHERE ref=?", (ref,), "one")
    if not row:
        return "unknown"
    if row["processed"]:
        return "duplicate"
    try:
        v = requests.get(f"{PS}/transaction/verify/{ref}", headers=ps_headers(), timeout=20).json()
    except Exception as e:
        print("verify error", e)
        return "error"
    d = (v.get("data") or {}) if v.get("status") else {}
    if d.get("status") != "success" or d.get("reference") != ref:
        return "unpaid"
    if d.get("amount") != AMOUNT_KOBO or d.get("currency") != "NGN":
        alert_admins(f"\U0001F6A8 <b>Payment mismatch - access NOT granted</b>\nRef: <code>{esc(ref)}</code>\n"
                     f"Paid: {esc(d.get('amount'))} {esc(d.get('currency'))} (expected {AMOUNT_KOBO} NGN)\n"
                     f"Student: {label(row['tg_id'])} (<code>{row['tg_id']}</code>)")
        return "mismatch"
    if db("UPDATE refs SET processed=1 WHERE ref=? AND processed=0", (ref,)) != 1:
        return "duplicate"
    uid, email = row["tg_id"], row["email"]
    exp = grant(uid, PLAN_DAYS, email)
    channel = d.get("channel") or "n/a"
    db("INSERT OR IGNORE INTO payments (ref,tg_id,email,amount,channel,paid_at) VALUES (?,?,?,?,?,?)",
       (ref, uid, email, PRICE_NAIRA, channel, now().isoformat()))
    send_access(uid, f"\u2705 <b>Payment confirmed - thank you!</b>\n\nAmount: {naira(PRICE_NAIRA)}\n"
                     f"Reference: <code>{esc(ref)}</code>\nAccess until: <b>{fdate(exp)}</b>")
    alert_admins(f"\U0001F4B0 <b>Payment received</b>: {naira(PRICE_NAIRA)}\nStudent: {label(uid)} (<code>{uid}</code>)\n"
                 f"Email: {esc(email)}\nVia: {esc(channel)}\nActive until: {fdate(exp)}")
    return "ok"


@app.route("/paystack", methods=["POST"])
def paystack_webhook():
    raw = request.get_data()
    sig = request.headers.get("x-paystack-signature", "")
    expected = hmac.new(PAYSTACK_SECRET.encode(), raw, hashlib.sha512).hexdigest()
    if not hmac.compare_digest(sig, expected):
        abort(401)
    try:
        event = json.loads(raw)
        if event.get("event") == "charge.success":
            d = event.get("data") or {}
            ref = d.get("reference", "")
            res = process_payment(ref)
            if res == "unknown":
                alert_admins(f"\u2139\ufe0f A payment arrived that did not start in the bot.\nRef: <code>{esc(ref)}</code>\n"
                             f"Email: {esc((d.get('customer') or {}).get('email'))}\nAmount: {naira((d.get('amount') or 0) / 100)}\n"
                             "If it is a student, use /grant TELEGRAM_ID 30")
            elif res == "unpaid":
                alert_admins(f"\u26a0\ufe0f Paystack sent success but verification disagrees. Access NOT granted.\n"
                             f"Ref: <code>{esc(ref)}</code>")
    except Exception:
        err_alert("paystack webhook")
    return "ok", 200


def check_payments(uid):
    """Student tapped 'I've paid': re-verify their recent unprocessed payments."""
    since = (now() - timedelta(days=3)).isoformat()
    refs = db("SELECT ref FROM refs WHERE tg_id=? AND processed=0 AND created>? ORDER BY created DESC",
              (uid, since), "all")
    return any(process_payment(r["ref"]) == "ok" for r in refs)


# ============================ Student screens ============================
PAY_BTN = f"\U0001F4B3 Pay {naira(PRICE_NAIRA)}"
STATUS_BTN = "\U0001F4C5 My status"
LINKS_BTN = "\U0001F517 My links"
HELP_BTN = "\u2753 Help"
CONTACT_BTN = "\U0001F4AC Contact me"
MAIN_KEYBOARD = {"keyboard": [[{"text": PAY_BTN}, {"text": STATUS_BTN}], [{"text": LINKS_BTN}, {"text": HELP_BTN}, {"text": CONTACT_BTN}]],
                 "resize_keyboard": True, "is_persistent": True}
RENEW_MARKUP = {"inline_keyboard": [[{"text": "\U0001F504 Renew now", "callback_data": "pay"}]]
                + ([[{"text": "\U0001F4AC Message me", "url": SUPPORT_URL}]] if SUPPORT_URL else [])}
awaiting_email = set()


def do_start(uid, frm):
    awaiting_email.discard(uid)
    row = get_sub(uid)
    extra = ""
    if row and not row["removed"] and parse_date(row["expiry"]) >= today():
        extra = f"\n\n\u2705 You are active until <b>{fdate(parse_date(row['expiry']))}</b>."
    send(uid, f"Hi {esc(frm.get('first_name') or 'there')}! \U0001F44B Welcome to <b>{esc(BUSINESS)}</b>.\n\n"
              f"{naira(PRICE_NAIRA)} gives you <b>{PLAN_DAYS} days</b> of access to the tutorial group and the "
              "materials channel.\n\n<b>How it works</b>\n1\ufe0f\u20e3 Tap <b>Pay</b> and type your email\n"
              "2\ufe0f\u20e3 Pay by card, bank transfer or USSD\n3\ufe0f\u20e3 Your join links arrive here automatically"
              "\n\nQuestions? Tap \U0001F4AC <b>Contact me</b> any time." + extra, MAIN_KEYBOARD)


def ask_email(uid):
    awaiting_email.add(uid)
    send(uid, "\U0001F4E7 Please type the email address for your payment receipt.", MAIN_KEYBOARD)


def do_pay(uid, email=None):
    email = (email or get_email(uid) or "").strip().lower()
    if not valid_email(email):
        if email:
            send(uid, "That does not look like a valid email.")
        ask_email(uid)
        return
    save_email(uid, email)
    awaiting_email.discard(uid)
    note = ""
    row = get_sub(uid)
    if row and not row["removed"] and parse_date(row["expiry"]) >= today():
        note = (f"You are active until <b>{fdate(parse_date(row['expiry']))}</b>. Renewing now "
                f"<b>adds {PLAN_DAYS} days on top</b> - you lose nothing.\n\n")
    url = start_payment(uid, email)
    if not url:
        send(uid, "Sorry, I could not create a payment link right now. Please try again in a minute.", MAIN_KEYBOARD)
        return
    send(uid, note + f"Tap below to pay <b>{naira(PRICE_NAIRA)}</b> for {PLAN_DAYS} days. Card, bank transfer and USSD all work.\n"
                     f"\U0001F4E7 Receipt email: {esc(email)}\n\nAfter paying, your join links arrive here automatically. "
                     "If they do not show up within a few minutes, tap <b>I have paid</b>.",
         {"inline_keyboard": [[{"text": f"\U0001F4B3 Pay {naira(PRICE_NAIRA)} now", "url": url}],
                              [{"text": "\u2705 I have paid - check now", "callback_data": "check"}],
                              [{"text": "\u270f\ufe0f Change email", "callback_data": "email"}]]
                             + ([[{"text": "\U0001F4AC Need help? Message me", "url": SUPPORT_URL}]] if SUPPORT_URL else [])})


def do_check(uid):
    if check_payments(uid):
        return  # send_access already messaged the student
    send(uid, "I do not see a confirmed payment yet. \u23f3 Bank transfers can take a few minutes. "
              "Try again shortly, and if it still does not show, contact support with your payment receipt.",
         support_markup())


def support_markup():
    if SUPPORT_URL:
        return {"inline_keyboard": [[{"text": "\U0001F4AC Message me on Telegram", "url": SUPPORT_URL}]]}
    return MAIN_KEYBOARD


def do_contact(uid):
    send(uid, "\U0001F4AC <b>Need help or have a question?</b>\n\nTap the button below to message me directly on "
              "Telegram. If it is about a payment, please include your receipt or reference.", support_markup())


def do_status(uid):
    row = get_sub(uid)
    if not row or row["removed"]:
        send(uid, "You do not have an active subscription yet. Tap <b>Pay</b> to get started \U0001F680", MAIN_KEYBOARD)
        return
    exp = parse_date(row["expiry"])
    d = (exp - today()).days
    if d >= 0:
        text = (f"\U0001F4C5 <b>Your subscription</b>\n\n\u2705 Active\nExpires: <b>{fdate(exp)}</b>\n"
                f"Days left: <b>{d}</b>\n{bar(d)}")
        if d <= REMIND_DAYS:
            text += "\n\n\u23f3 Renew early and the days add on top."
    else:
        left = GRACE_DAYS + d + 1
        text = (f"\U0001F4C5 <b>Your subscription</b>\n\n\u26a0\ufe0f Expired {-d} day(s) ago ({fdate(exp)})\n"
                f"Access ends in <b>{left} day(s)</b>. Renew now to stay in.")
    send(uid, text, RENEW_MARKUP if d <= REMIND_DAYS else MAIN_KEYBOARD)


def do_links(uid):
    row = get_sub(uid)
    if row and not row["removed"] and parse_date(row["expiry"]) >= today():
        links, errs = invite_links()
        if links:
            send(uid, "Here are your fresh one-time join links (valid 24 hours):",
                 {"inline_keyboard": [[{"text": t, "url": u}] for t, u in links]})
        else:
            alert_admins(f"\u26a0\ufe0f Could not create links for {label(uid)}: {esc('; '.join(errs))}")
            send(uid, "I could not create your links right now. The admin has been alerted.", MAIN_KEYBOARD)
    elif row and not row["removed"]:
        send(uid, "Your subscription has expired. Renew to get new links.", RENEW_MARKUP)
    else:
        send(uid, "You need an active subscription first. Tap <b>Pay</b> to subscribe.", MAIN_KEYBOARD)


def do_receipts(uid):
    rows = db("SELECT * FROM payments WHERE tg_id=? ORDER BY paid_at DESC LIMIT 5", (uid,), "all")
    if not rows:
        send(uid, "No payments found yet.", MAIN_KEYBOARD)
        return
    lines = [f"\u2022 {naira(r['amount'])} on {fdate(datetime.fromisoformat(r['paid_at']).date())} "
             f"(<code>{esc(r['ref'])}</code>)" for r in rows]
    send(uid, "\U0001F9FE <b>Your last payments</b>\n\n" + "\n".join(lines), MAIN_KEYBOARD)


def do_help(uid):
    send(uid, "\u2753 <b>Help</b>\n\n<b>How long is access?</b> " + f"{PLAN_DAYS} days per payment.\n\n"
              "<b>How do I pay?</b> Tap Pay, type your email, and use the button. Card, bank transfer and USSD work.\n\n"
              "<b>I paid but got no links.</b> Tap \u201cI have paid\u201d under the payment message, or wait a few minutes.\n\n"
              "<b>My link expired.</b> Tap \U0001F517 My links for a fresh one.\n\n"
              f"<b>Can I renew early?</b> Yes. The {PLAN_DAYS} days are added on top of what you have left.\n\n"
              "<b>Reminders:</b> I message you before your plan ends and for a few days after."
              + (f"\n\nNeed a human? {esc(SUPPORT)}" if SUPPORT else ""), support_markup())


# ============================== Admin tools ==============================
ADMIN_CMDS = {"/admin", "/stats", "/members", "/expiring", "/find", "/grant", "/extend", "/revoke",
              "/broadcast", "/announce", "/export", "/backup"}


def stats_text():
    t = today()
    subs = db("SELECT tg_id, expiry FROM subs WHERE removed=0", (), "all")
    active = soon = grace = unreachable = 0
    for r in subs:
        d = (parse_date(r["expiry"]) - t).days
        if d >= 0:
            active += 1
            soon += 1 if d <= 7 else 0
        else:
            grace += 1
        u = db("SELECT blocked FROM users WHERE tg_id=?", (r["tg_id"],), "one")
        if u is None or u["blocked"]:
            unreachable += 1
    ym, ymd = t.strftime("%Y-%m"), t.isoformat()
    rm = db("SELECT COUNT(*) c, COALESCE(SUM(amount),0) s FROM payments WHERE substr(paid_at,1,7)=?", (ym,), "one")
    rt = db("SELECT COUNT(*) c, COALESCE(SUM(amount),0) s FROM payments WHERE substr(paid_at,1,10)=?", (ymd,), "one")
    ra = db("SELECT COUNT(*) c, COALESCE(SUM(amount),0) s FROM payments", (), "one")
    users = db("SELECT COUNT(*) c FROM users", (), "one")["c"]
    text = (f"\U0001F4CA <b>Stats</b>\n\nActive members: <b>{active}</b>\nExpiring within 7 days: <b>{soon}</b>\n"
            f"In grace period: <b>{grace}</b>\n\nToday: {naira(rt['s'])} ({rt['c']} payments)\n"
            f"This month: {naira(rm['s'])} ({rm['c']} payments)\nAll time: {naira(ra['s'])} ({ra['c']} payments)\n\n"
            f"People who started the bot: {users}")
    if unreachable:
        text += (f"\n\n\u26a0\ufe0f {unreachable} member(s) cannot receive my messages (they have not started the bot "
                 "or blocked it), so they will get no reminders.")
    return text


def member_lines(rows):
    t = today()
    out = []
    for r in rows:
        d = (parse_date(r["expiry"]) - t).days
        flag = "\u26a0\ufe0f" if d < 0 else ("\u23f3" if d <= REMIND_DAYS else "\u2705")
        out.append(f"{flag} {label(r['tg_id'])} <code>{r['tg_id']}</code> - {fdate(parse_date(r['expiry']))} ({d}d)")
    return out


def send_long(uid, text):
    for i in range(0, len(text), 3800):
        send(uid, text[i:i + 3800])


def do_members(uid):
    rows = db("SELECT tg_id, expiry FROM subs WHERE removed=0 ORDER BY expiry", (), "all")
    send_long(uid, f"\U0001F465 <b>Members: {len(rows)}</b>\n\n" + ("\n".join(member_lines(rows)) or "None yet."))


def do_expiring(uid, days=7):
    end = (today() + timedelta(days=days)).isoformat()
    rows = db("SELECT tg_id, expiry FROM subs WHERE removed=0 AND expiry<=? ORDER BY expiry", (end,), "all")
    send_long(uid, f"\u23f3 <b>Expiring within {days} days (and overdue): {len(rows)}</b>\n\n"
              + ("\n".join(member_lines(rows)) or "Nobody."))


def do_find(uid, q):
    q = q.strip()
    if q.lstrip("-").isdigit():
        row = db("SELECT tg_id FROM users WHERE tg_id=? UNION SELECT tg_id FROM subs WHERE tg_id=?", (int(q), int(q)), "one")
    elif q.startswith("@"):
        row = db("SELECT tg_id FROM users WHERE username=?", (q[1:].lower(),), "one")
    else:
        row = db("SELECT tg_id FROM emails WHERE lower(email)=? ", (q.lower(),), "one")
    if not row:
        send(uid, "Nobody found. Use: /find 123456789, /find @username or /find email")
        return
    t = row["tg_id"]
    sub = get_sub(t)
    pay = db("SELECT COUNT(*) c, COALESCE(SUM(amount),0) s FROM payments WHERE tg_id=?", (t,), "one")
    if sub and not sub["removed"]:
        d = (parse_date(sub["expiry"]) - today()).days
        state = f"Active until {fdate(parse_date(sub['expiry']))} ({d} days)"
    elif sub:
        state = "Removed (expired)"
    else:
        state = "Never subscribed"
    send(uid, f"\U0001F50E <b>{label(t)}</b>\nID: <code>{t}</code>\nEmail: {esc(get_email(t) or 'not given')}\n"
              f"Status: {state}\nPayments: {pay['c']} ({naira(pay['s'])})")


def export_csv():
    out = io.StringIO()
    w = csv.writer(out)
    w.writerow(["telegram_id", "name", "username", "email", "expires", "days_left", "status"])
    rows = db("SELECT s.tg_id, s.expiry, s.removed, e.email, u.first_name, u.username FROM subs s "
              "LEFT JOIN emails e ON e.tg_id=s.tg_id LEFT JOIN users u ON u.tg_id=s.tg_id ORDER BY s.expiry", (), "all")
    for r in rows:
        d = (parse_date(r["expiry"]) - today()).days
        status = "removed" if r["removed"] else ("active" if d >= 0 else "grace")
        w.writerow([r["tg_id"], r["first_name"] or "", r["username"] or "", r["email"] or "", r["expiry"], d, status])
    return out.getvalue().encode("utf-8-sig")


def backup_bytes():
    tmp = DB_PATH + ".bak"
    with lock:
        src, dst = sqlite3.connect(DB_PATH), sqlite3.connect(tmp)
        try:
            src.backup(dst)
        finally:
            dst.close()
            src.close()
    with open(tmp, "rb") as f:
        data = f.read()
    try:
        os.remove(tmp)
    except OSError:
        pass
    return data


def bulk_send(ids, body, admin_id):
    sent = failed = 0
    for i in ids:
        if send(i, body, html_mode=False):
            sent += 1
        else:
            failed += 1
        time.sleep(0.05)
    send(admin_id, f"\U0001F4E3 Broadcast finished: {sent} delivered, {failed} could not be reached.")


def do_admin_menu(uid):
    send(uid, "\U0001F6E0 <b>Admin panel</b>\n\n"
              "/stats - money and members at a glance\n/members - everyone active\n/expiring 7 - who is about to expire\n"
              "/find ID, @username or email\n/grant ID 30 - give or extend access\n/revoke ID - remove someone now\n"
              "/broadcast message - message active members\n/announce message - message everyone who started the bot\n"
              "/export - spreadsheet of members\n/backup - download the database",
         {"inline_keyboard": [[{"text": "\U0001F4CA Stats", "callback_data": "a:stats"},
                               {"text": "\U0001F465 Members", "callback_data": "a:members"}],
                              [{"text": "\u23f3 Expiring", "callback_data": "a:expiring"},
                               {"text": "\U0001F4E4 Export CSV", "callback_data": "a:export"}],
                              [{"text": "\U0001F4BE Backup", "callback_data": "a:backup"}]]})


def admin_command(uid, cmd, rest, arg_text):
    if cmd == "/admin":
        do_admin_menu(uid)
    elif cmd == "/stats":
        send(uid, stats_text())
    elif cmd == "/members":
        do_members(uid)
    elif cmd == "/expiring":
        do_expiring(uid, int(rest[0]) if rest and rest[0].isdigit() else 7)
    elif cmd == "/find":
        do_find(uid, arg_text)
    elif cmd in ("/grant", "/extend"):
        try:
            target = int(rest[0])
            days = int(rest[1]) if len(rest) > 1 else PLAN_DAYS
            exp = grant(target, days)
            ok = send_access(target, f"\U0001F381 <b>Access granted</b>\nYou now have access until <b>{fdate(exp)}</b>.")
            send(uid, f"Done \u2705 <code>{target}</code> is active until {fdate(exp)}."
                 + ("" if ok else "\n\u26a0\ufe0f I could not message them - they must open the bot and tap Start first. "
                                  "Then ask them to tap \U0001F517 My links."))
        except Exception:
            send(uid, "Use: /grant TELEGRAM_ID 30")
    elif cmd == "/revoke":
        try:
            target = int(rest[0])
            remove_member(target)
            db("UPDATE subs SET removed=1 WHERE tg_id=?", (target,))
            send(uid, f"\u2705 <code>{target}</code> removed from the group and channel.")
        except Exception:
            send(uid, "Use: /revoke TELEGRAM_ID")
    elif cmd in ("/broadcast", "/announce"):
        if not arg_text:
            send(uid, f"Use: {cmd} your message")
            return
        if cmd == "/broadcast":
            ids = [r["tg_id"] for r in db("SELECT tg_id FROM subs WHERE removed=0", (), "all")]
        else:
            ids = [r["tg_id"] for r in db("SELECT tg_id FROM users WHERE blocked=0", (), "all")]
        send(uid, f"\U0001F4E3 Sending to {len(ids)} people...")
        threading.Thread(target=bulk_send, args=(ids, arg_text, uid), daemon=True).start()
    elif cmd == "/export":
        send_document(uid, f"members_{today().isoformat()}.csv", export_csv(), "Members spreadsheet (opens in Excel/Sheets)")
    elif cmd == "/backup":
        send_document(uid, f"backup_{today().isoformat()}.db", backup_bytes(), "Database backup - keep it safe and private")


# ============================ Telegram webhook ============================
_seen = deque(maxlen=1000)


def on_message(msg):
    if msg.get("chat", {}).get("type") != "private":
        return
    frm = msg.get("from") or {}
    uid = frm.get("id")
    if not uid or frm.get("is_bot"):
        return
    record_user(frm)
    text = (msg.get("text") or "").strip()
    if not text:
        return
    cmd, rest = "", []
    if text.startswith("/"):
        parts = text.split()
        cmd, rest = parts[0].split("@")[0].lower(), parts[1:]
    pieces = text.split(None, 1)
    arg_text = pieces[1].strip() if len(pieces) > 1 else ""

    if cmd == "/start":
        do_start(uid, frm)
    elif cmd == "/pay" or text == PAY_BTN:
        do_pay(uid, rest[0] if rest else None)
    elif cmd == "/email":
        ask_email(uid)
    elif cmd == "/status" or text == STATUS_BTN:
        do_status(uid)
    elif cmd == "/links" or text == LINKS_BTN:
        do_links(uid)
    elif cmd == "/receipts":
        do_receipts(uid)
    elif cmd == "/help" or text == HELP_BTN:
        do_help(uid)
    elif cmd == "/contact" or text == CONTACT_BTN:
        do_contact(uid)
    elif cmd == "/cancel":
        awaiting_email.discard(uid)
        send(uid, "Cancelled.", MAIN_KEYBOARD)
    elif uid in ADMIN_IDS and cmd in ADMIN_CMDS:
        admin_command(uid, cmd, rest, arg_text)
    elif uid in awaiting_email:
        email = text.strip().lower()
        if valid_email(email):
            do_pay(uid, email)
        else:
            send(uid, "That does not look like an email. Please type it again, e.g. name@gmail.com (or /cancel).")
    else:
        send(uid, "I did not catch that. Please use the buttons below \U0001F447", MAIN_KEYBOARD)


def on_callback(cq):
    tg("answerCallbackQuery", callback_query_id=cq["id"])
    frm = cq["from"]
    uid, data = frm["id"], cq.get("data", "")
    record_user(frm)
    if data == "pay":
        do_pay(uid)
    elif data == "check":
        do_check(uid)
    elif data == "email":
        ask_email(uid)
    elif data.startswith("a:") and uid in ADMIN_IDS:
        what = data[2:]
        if what == "stats":
            send(uid, stats_text())
        elif what == "members":
            do_members(uid)
        elif what == "expiring":
            do_expiring(uid)
        elif what == "export":
            admin_command(uid, "/export", [], "")
        elif what == "backup":
            admin_command(uid, "/backup", [], "")


def on_chat_member(cm):
    chat_id = str(cm.get("chat", {}).get("id"))
    names = {str(GROUP_ID): "the group", str(CHANNEL_ID): "the channel"}
    if chat_id not in names or not chat_id.strip("-"):
        return
    new, old = cm["new_chat_member"], cm["old_chat_member"]
    user = new["user"]
    if user.get("is_bot") or new["status"] not in ("member", "restricted") or old["status"] not in ("left", "kicked"):
        return
    uid = user["id"]
    if uid in ADMIN_IDS:
        return
    sub = get_sub(uid)
    if sub and not sub["removed"]:
        return
    who = f"{esc(user.get('first_name') or 'Someone')} (<code>{uid}</code>)"
    if GATEKEEPER:
        remove_from(chat_id, uid)
        alert_admins(f"\U0001F6AB Removed {who}: joined {names[chat_id]} without an active subscription.")
        send(uid, "You need an active subscription to join. Open me and tap <b>Pay</b> to subscribe.")
    else:
        alert_admins(f"\U0001F440 {who} joined {names[chat_id]} without an active subscription.\n"
                     f"Remove with /revoke {uid}, or set GATEKEEPER=on to auto-remove.")


@app.route("/telegram", methods=["POST"])
def telegram_webhook():
    if request.headers.get("X-Telegram-Bot-Api-Secret-Token") != TG_SECRET:
        abort(401)
    upd = request.get_json(silent=True) or {}
    uid = upd.get("update_id")
    if uid in _seen:
        return "ok", 200
    _seen.append(uid)
    try:
        if "message" in upd:
            on_message(upd["message"])
        elif "callback_query" in upd:
            on_callback(upd["callback_query"])
        elif "chat_member" in upd:
            on_chat_member(upd["chat_member"])
    except Exception:
        err_alert("telegram handler")
    return "ok", 200


@app.route("/")
def home():
    return "Bot is running", 200


@app.route("/health")
def health():
    return jsonify(ok=True)


# ================== Background jobs: reminders, healing, summaries ==================
def reconcile_and_nudge():
    since = (now() - timedelta(hours=24)).isoformat()
    for r in db("SELECT * FROM refs WHERE processed=0 AND created>?", (since,), "all"):
        age = now() - datetime.fromisoformat(r["created"])
        if age < timedelta(minutes=2):
            continue
        if age < timedelta(hours=6) and process_payment(r["ref"]) == "ok":
            continue
        if age >= timedelta(minutes=60) and not r["nudged"]:
            db("UPDATE refs SET nudged=1 WHERE ref=?", (r["ref"],))
            later = db("SELECT 1 FROM refs WHERE tg_id=? AND processed=1 AND created>?", (r["tg_id"], r["created"]), "one")
            if not later:
                send(r["tg_id"], "Hey \U0001F44B I noticed you started a payment but it did not go through. "
                                 "Need a hand? You can try again below.",
                     {"inline_keyboard": [[{"text": "\U0001F504 Try again", "callback_data": "pay"}]]
                                          + ([[{"text": "\U0001F4AC Message me", "url": SUPPORT_URL}]] if SUPPORT_URL else [])})


def daily_job():
    t = today()
    removed_today = []
    for row in db("SELECT * FROM subs WHERE removed=0", (), "all"):
        d = (parse_date(row["expiry"]) - t).days
        uid = row["tg_id"]
        name = esc(first_name(uid))
        if d < -GRACE_DAYS:
            remove_member(uid)
            db("UPDATE subs SET removed=1 WHERE tg_id=?", (uid,))
            removed_today.append(uid)
            send(uid, f"Hi {name}, your subscription ended and you were removed from the group and channel. "
                      "Renew any time to come back \U0001F499", RENEW_MARKUP)
        elif d <= REMIND_DAYS and row["last_reminded"] != t.isoformat():
            if d > 1:
                text = f"\u23f0 Hi {name}! Your subscription ends in <b>{d} days</b> ({fdate(parse_date(row['expiry']))})."
            elif d == 1:
                text = f"\u23f0 Hi {name}! Your subscription ends <b>tomorrow</b>."
            elif d == 0:
                text = f"\u23f0 Hi {name}! Your subscription ends <b>today</b>."
            else:
                text = (f"\u26a0\ufe0f Hi {name}, your subscription expired {-d} day(s) ago. "
                        f"You will be removed in <b>{GRACE_DAYS + d + 1} day(s)</b>.")
            send(uid, text + f"\nRenew now - the {PLAN_DAYS} days add on top of what you have left.", RENEW_MARKUP)
            db("UPDATE subs SET last_reminded=? WHERE tg_id=?", (t.isoformat(), uid))
    summary = f"\u2600\ufe0f <b>Daily summary - {fdate(t)}</b>\n\n" + stats_text()
    if removed_today:
        summary += "\n\n\U0001F6AA Removed today: " + ", ".join(f"<code>{x}</code>" for x in removed_today)
    alert_admins(summary)
    if t.weekday() == 0:
        data = backup_bytes()
        for a in ADMIN_IDS:
            send_document(a, f"weekly_backup_{t.isoformat()}.db", data, "Weekly backup - keep it safe and private")


def scheduler():
    while True:
        try:
            reconcile_and_nudge()
        except Exception:
            err_alert("reconcile")
        try:
            n = now()
            last = db("SELECT v FROM meta WHERE k='last_run'", (), "one")
            if n.hour >= SUMMARY_HOUR and (not last or last["v"] != n.date().isoformat()):
                db("INSERT INTO meta (k,v) VALUES ('last_run',?) ON CONFLICT(k) DO UPDATE SET v=?",
                   (n.date().isoformat(),) * 2)
                daily_job()
        except Exception:
            err_alert("daily job")
        time.sleep(300)


def setup():
    global BOT_USERNAME
    me = tg("getMe")
    if me.get("ok"):
        BOT_USERNAME = me["result"].get("username", "")
    tg("setMyCommands", commands=[
        {"command": "start", "description": "Welcome and subscribe"},
        {"command": "pay", "description": f"Pay {naira(PRICE_NAIRA)} for {PLAN_DAYS} days"},
        {"command": "status", "description": "Check your days left"},
        {"command": "links", "description": "Get your join links again"},
        {"command": "receipts", "description": "See your payments"},
        {"command": "help", "description": "How it works"},
        {"command": "contact", "description": "Message the teacher"}])
    for a in ADMIN_IDS:
        tg("setMyCommands", scope={"type": "chat", "chat_id": a}, commands=[
            {"command": "admin", "description": "Admin panel"},
            {"command": "stats", "description": "Money and members"},
            {"command": "members", "description": "Active members"},
            {"command": "expiring", "description": "Who expires soon"},
            {"command": "find", "description": "Look someone up"},
            {"command": "grant", "description": "Give access: /grant ID 30"},
            {"command": "revoke", "description": "Remove: /revoke ID"},
            {"command": "broadcast", "description": "Message active members"},
            {"command": "announce", "description": "Message everyone"},
            {"command": "export", "description": "Members spreadsheet"},
            {"command": "backup", "description": "Download database"},
            {"command": "start", "description": "Student view"}])
    tg("setMyShortDescription", short_description=f"{BUSINESS}: subscribe and get instant access."[:120])
    tg("setMyDescription", description=(f"Welcome to {BUSINESS}! Subscribe for {naira(PRICE_NAIRA)} / {PLAN_DAYS} days to get "
                                        "instant access to the tutorial group and materials channel. Tap Start to begin.")[:500])
    if PUBLIC_URL:
        tg("setWebhook", url=f"{PUBLIC_URL}/telegram", secret_token=TG_SECRET,
           allowed_updates=["message", "callback_query", "chat_member"])
    threading.Thread(target=scheduler, daemon=True).start()


setup()
