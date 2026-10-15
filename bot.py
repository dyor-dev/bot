import os
import re
import json
import time
import random
import asyncio
import ctypes

# Python 3.12 va Pyrogram to'qnashuvini to'g'irlash
try:
    asyncio.get_event_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

# RAM qulflash
try:
    MCL_CURRENT = 1
    MCL_FUTURE = 2
    libc = ctypes.CDLL("libc.so.6")
    libc.mlockall(MCL_CURRENT | MCL_FUTURE)
except Exception:
    pass

from pyrogram import Client, filters
from pyrogram.raw import functions, types

# =========================
# SOZLAMALAR
# =========================
API_ID = 12203269
API_HASH = "5bfb8b0e68d86a267afe2ebe87fb2335"

# O'ZINGIZNING YANGI AQ... BILAN BOSHLANADIGAN SESSIA KODINGIZ:
SESSION_STRING = "1ApWapzMBuwp9InwRreFMxKrFXcTR3cZ9jEcJ29V41p7pljIaa5-xc7tM-afJgLhPVLaJdkYlnJIYwzWueZY6AWyiYooSlGDB2WPqDaROyJppTV6JLT3E1nJat7sRVOrh4Ic28lBOnfNUprh24w1ygSFek0as3VeXtxkhosTGb2FLIIoyxeCsqvCD8NnFY1ABcSmZIt6VounfuWT9ruemTWn98tvJiS3ypKtn_Y-hvgp_y85ZDiKDrv630WkJ24Ekr2WSLQtLsn3MgLZ2Lb-Hpb90AkcD3r4b9jQu_2hOkLfg8XCYnGIMiri-mZMbumr071UaXXhBNhhC1bMsv1t-QhIPEOMDMuY="

CHANNELS_FILE = "/home/ubuntu/channels.json"
COMMENTS_FILE = "/home/ubuntu/comments.json"
DEFAULT_CHANNEL = "aslamboi"
# =========================

app = Client(
    "pyro_sniper",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING,
    in_memory=True
)

CHANNELS_MAP = {}
GROUPS_MAP = {}
COMMENTS = []

SNIPER_MODE = "auto"
TARGET_POST_NUM = 1
POST_COUNTER = 0
LIMIT_REMAINING = 0
DELAY_SETTING = "instant"

sniped_posts = set()

def load_saved_channels():
    if os.path.exists(CHANNELS_FILE):
        try:
            with open(CHANNELS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return [DEFAULT_CHANNEL]

def save_channels_to_file(channels_list):
    with open(CHANNELS_FILE, "w", encoding="utf-8") as f:
        json.dump(channels_list, f, ensure_ascii=False, indent=2)

def load_saved_comments():
    if os.path.exists(COMMENTS_FILE):
        try:
            with open(COMMENTS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return []

def save_comments_to_file(comments_list):
    with open(COMMENTS_FILE, "w", encoding="utf-8") as f:
        json.dump(comments_list, f, ensure_ascii=False, indent=2)

async def register_channel(username_or_id):
    try:
        chat = await app.get_chat(username_or_id)
        if not chat.linked_chat:
            return False, "Discussion guruhi ulanmagan!"
        
        c_id = int(str(chat.id).replace("-100", ""))
        g_id = int(str(chat.linked_chat.id).replace("-100", ""))
        
        CHANNELS_MAP[c_id] = {
            "title": chat.title,
            "username": getattr(chat, 'username', str(c_id)),
            "full_id": chat.id,
            "group_full_id": chat.linked_chat.id,
            "group_id": g_id
        }
        GROUPS_MAP[g_id] = c_id
        return True, f"Qo'shildi: {chat.title}"
    except Exception as e:
        return False, str(e)

async def smart_active_heartbeat():
    while True:
        await asyncio.sleep(25)
        try:
            await app.invoke(functions.updates.GetState())
        except Exception:
            pass

# ==========================================
# 📸 .WOW
# ==========================================
@app.on_message(filters.me & filters.command("wow", prefixes="."))
async def wow_media_saver(client, message):
    reply_msg = message.reply_to_message
    try:
        await message.delete()
    except Exception:
        pass

    if not reply_msg or not (reply_msg.photo or reply_msg.video or reply_msg.document or reply_msg.animation):
        return

    async def _async_save():
        try:
            file_path = await client.download_media(reply_msg)
            if not file_path:
                return
            ttl = getattr(reply_msg, "ttl_seconds", None)
            ttl_str = "1 martalik (View-Once) 🔥" if ttl == 2147483647 else (f"{ttl} soniya ⏳" if ttl else "Oddiy media")
            caption = f"📸 **Media saqlandi!** (.wow)\n⏳ **Taymer:** {ttl_str}"
            await client.send_document("me", file_path, caption=caption)
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f"[!] .wow xatolik: {e}", flush=True)

    asyncio.create_task(_async_save())

# ==========================================
# 📝 .WORD
# ==========================================
@app.on_message(filters.me & filters.command("word", prefixes="."))
async def word_manager_handler(client, message):
    global COMMENTS
    text_content = message.text or ""
    parts_cmd = text_content.split(maxsplit=1)
    
    if len(parts_cmd) < 2 or not parts_cmd[1].strip():
        if not COMMENTS:
            await message.edit_text("ℹ️ Hozirda birorta ham komment saqlanmagan.\n\nFoydalanish:\n.word\n1. Gap bir\n2. Gap ikki")
            return
        res = f"📝 **Hozirgi mavjud so'zlar ({len(COMMENTS)} ta):**\n\n"
        for i, w in enumerate(COMMENTS, 1):
            first_line = w.splitlines()[0]
            res += f"`{i}.` {first_line}\n"
        await message.edit_text(res)
        return

    raw_text = parts_cmd[1].strip()
    parts = re.split(r'(?:\r?\n|^)\s*\d+[\.\)]\s*', raw_text)
    new_words = [p.strip() for p in parts if p.strip()]

    if not new_words:
        new_words = [line.strip() for line in raw_text.splitlines() if line.strip()]

    if not new_words:
        await message.edit_text("❌ So'zlar aniqlanmadi!")
        return

    COMMENTS = new_words
    save_comments_to_file(COMMENTS)

    preview = "\n".join([f"`{i}.` {w.splitlines()[0]}" for i, w in enumerate(COMMENTS[:5], 1)])
    more_text = f"\n... va yana {len(COMMENTS) - 5} ta" if len(COMMENTS) > 5 else ""
    await message.edit_text(f"✅ **Yangi ro'yxat saqlandi ({len(COMMENTS)} ta so'z/gap)!**\nEskisi butunlay o'chirildi.\n\n{preview}{more_text}")

# ==========================================
# 🏓 RAQOBATCHIDEK PING (.ping)
# ==========================================
@app.on_message(filters.me & filters.command("ping", prefixes="."))
async def ping_cmd(client, message):
    start = time.perf_counter()
    await message.edit_text("🏓 Pong!")
    end = time.perf_counter()
    ms = round((end - start) * 1000, 1)
    await message.edit_text(f"🏓 Pong! {ms} ms")

# =========================
# BUYRUQLAR
# =========================
@app.on_message(filters.me & filters.command("shot", prefixes="."))
async def shot_handler(client, message):
    global SNIPER_MODE, TARGET_POST_NUM, POST_COUNTER
    SNIPER_MODE = "target"
    TARGET_POST_NUM = 1
    POST_COUNTER = 0
    await message.edit_text("🎯 **1 MARTALIK ZARBA!**\nKeyingi 1-postga yozadi va avtomat to'xtaydi.")

@app.on_message(filters.me & filters.command("target", prefixes="."))
async def target_handler(client, message):
    global SNIPER_MODE, TARGET_POST_NUM, POST_COUNTER
    try:
        num = int(message.command[1])
        if num <= 0:
            raise ValueError
        SNIPER_MODE = "target"
        TARGET_POST_NUM = num
        POST_COUNTER = 0
        await message.edit_text(f"🎯 **Nishon: {num}-post!**\nOldingi postlarni o'tkazib, aynan {num}-postga yozadi va to'xtaydi.")
    except Exception:
        await message.edit_text("❌ Foydalanish: `.target 2`")

@app.on_message(filters.me & filters.command(["auto", "resume"], prefixes="."))
async def auto_handler(client, message):
    global SNIPER_MODE
    SNIPER_MODE = "auto"
    await message.edit_text("⚡ **DOIMIY AVTO-REJIM YOQILDI!**")

@app.on_message(filters.me & filters.command("pause", prefixes="."))
async def pause_handler(client, message):
    global SNIPER_MODE
    SNIPER_MODE = "paused"
    await message.edit_text("⏸ **Snayper to'liq PAUZAga qo'yildi!**")

@app.on_message(filters.me & filters.command("delay", prefixes="."))
async def delay_handler(client, message):
    global DELAY_SETTING
    cmd = message.command
    arg = cmd[1].lower() if len(cmd) > 1 else ""
    if arg in ("0", "instant", ""):
        DELAY_SETTING = "instant"
        await message.edit_text("⚡ **Kechikish: 0 soniya (Maksimal tezlik)!**")
    elif arg == "random":
        DELAY_SETTING = "random"
        await message.edit_text("🎲 **Kechikish: Random (0.5s - 2.5s oralig'ida)!**")
    else:
        try:
            sec = float(arg)
            DELAY_SETTING = sec
            await message.edit_text(f"⏱ **Kechikish: {sec} soniya!**")
        except ValueError:
            await message.edit_text("❌ Format xato! Masalan: `.delay 0`, `.delay random`, `.delay 1.5`")

@app.on_message(filters.me & filters.command("add", prefixes="."))
async def add_channel_handler(client, message):
    try:
        target = message.command[1].replace("@", "")
        await message.edit_text(f"⏳ `@{target}` tekshirilmoqda...")
        ok, msg = await register_channel(target)
        if ok:
            saved = load_saved_channels()
            if target not in saved:
                saved.append(target)
                save_channels_to_file(saved)
            await message.edit_text(f"✅ **Kanal qo'shildi!**\n🎯 {msg}")
        else:
            await message.edit_text(f"❌ **Xatolik:** {msg}")
    except Exception:
        await message.edit_text("❌ Foydalanish: `.add @kanal`")

@app.on_message(filters.me & filters.command("remove", prefixes="."))
async def remove_channel_handler(client, message):
    try:
        target = message.command[1].replace("@", "")
        saved = load_saved_channels()
        target_id = None
        for cid, data in list(CHANNELS_MAP.items()):
            if data['username'].lower() == target.lower() or str(cid) == target:
                target_id = cid
                break
        if target_id and target_id in CHANNELS_MAP:
            gid = CHANNELS_MAP[target_id]['group_id']
            del CHANNELS_MAP[target_id]
            if gid in GROUPS_MAP:
                del GROUPS_MAP[gid]
            saved = [c for c in saved if c.lower() != target.lower()]
            save_channels_to_file(saved)
            await message.edit_text(f"🗑 **O'chirildi:** `@{target}`")
        else:
            await message.edit_text("❌ Ro'yxatda topilmadi!")
    except Exception:
        await message.edit_text("❌ Foydalanish: `.remove @kanal`")

@app.on_message(filters.me & filters.command("channels", prefixes="."))
async def list_handler(client, message):
    if not CHANNELS_MAP:
        await message.edit_text("ℹ️ Hozirda nishondagi kanal yo'q.")
        return
    text = "🎯 **Faol Snayper Kanallari:**\n\n"
    for idx, (cid, data) in enumerate(CHANNELS_MAP.items(), 1):
        text += f"{idx}. **{data['title']}** (@{data['username']})\n"
    await message.edit_text(text)

# ⚡ ZERO-SECOND STRIKE
async def execute_zero_second_strike(chat_id, reply_id, post_id):
    global SNIPER_MODE, POST_COUNTER, LIMIT_REMAINING

    if post_id in sniped_posts or SNIPER_MODE == "paused":
        return
    sniped_posts.add(post_id)

    if SNIPER_MODE == "target":
        POST_COUNTER += 1
        if POST_COUNTER < TARGET_POST_NUM:
            return
        SNIPER_MODE = "paused"
    elif SNIPER_MODE == "limit":
        LIMIT_REMAINING -= 1
        if LIMIT_REMAINING <= 0:
            SNIPER_MODE = "paused"

    if DELAY_SETTING == "random":
        await asyncio.sleep(random.uniform(0.5, 2.5))
    elif isinstance(DELAY_SETTING, (int, float)) and DELAY_SETTING > 0:
        await asyncio.sleep(DELAY_SETTING)

    try:
        sent = await app.send_message(chat_id, ".", reply_to_message_id=reply_id)
        print(f"[🔥 PYROGRAM STRIKE] Post #{post_id} ga nuqta ketdi!", flush=True)

        async def _edit_bg():
            if COMMENTS:
                chosen = random.choice(COMMENTS)
                await sent.edit_text(chosen)
                print(f"[✏️ TAHRIRLANDI] -> '{chosen[:30]}...'", flush=True)

        asyncio.create_task(_edit_bg())
    except Exception as e:
        print(f"[!] Zarba xatosi: {e}", flush=True)

@app.on_message(filters.channel)
async def channel_post_listener(client, message):
    if SNIPER_MODE == "paused":
        return
    raw_cid = int(str(message.chat.id).replace("-100", ""))
    if raw_cid in CHANNELS_MAP:
        try:
            disc_msg = await client.get_discussion_message(message.chat.id, message.id)
            if disc_msg:
                await execute_zero_second_strike(disc_msg.chat.id, disc_msg.id, message.id)
        except Exception:
            pass

@app.on_message(filters.group)
async def group_post_listener(client, message):
    if SNIPER_MODE == "paused":
        return
    raw_gid = int(str(message.chat.id).replace("-100", ""))
    if raw_gid in GROUPS_MAP:
        target_cid = GROUPS_MAP[raw_gid]
        fwd_id = getattr(message.forward_from_chat, 'id', None)
        sender_id = getattr(message.sender_chat, 'id', None)
        fwd_raw = int(str(fwd_id).replace("-100", "")) if fwd_id else None
        sender_raw = int(str(sender_id).replace("-100", "")) if sender_id else None
        
        orig_post_id = message.forward_from_message_id or message.id
        if fwd_raw == target_cid or sender_raw == target_cid:
            await execute_zero_second_strike(message.chat.id, message.id, orig_post_id)

async def main():
    global COMMENTS
    print("[+] Pyrogram C-Dvigateli ishga tushmoqda...", flush=True)
    await app.start()

    saved_chans = load_saved_channels()
    COMMENTS = load_saved_comments()
    
    for ch in saved_chans:
        await register_channel(ch)
        
    print(f"👑 PYROGRAM C-SNAYPER TAYYOR ({len(CHANNELS_MAP)} kanal, {len(COMMENTS)} so'z)!\n", flush=True)
    asyncio.create_task(smart_active_heartbeat())

    # To'xtamasdan ishlash
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
