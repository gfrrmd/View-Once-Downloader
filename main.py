import os
import io
import json
import asyncio
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    filters, ContextTypes, ConversationHandler
)
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.errors import SessionPasswordNeededError, PhoneCodeInvalidError, PhoneCodeExpiredError
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument

BOT_TOKEN = os.environ["BOT_TOKEN"]
SESSION_FILE = "session_data.json"

API_ID_STEP, API_HASH_STEP, PHONE_STEP, CODE_STEP, PASSWORD_STEP = range(5)

DEVICE_MODEL = "iPhone 17 Pro Max"
SYSTEM_VERSION = "iOS 18.3.2"
APP_VERSION = "11.4.1"
LANG_CODE = "id"
SYSTEM_LANG_CODE = "id-ID"

temp_store = {}
userbot_client = None


def load_session():
    if os.path.exists(SESSION_FILE):
        with open(SESSION_FILE, "r") as f:
            return json.load(f)
    return None


def save_session(api_id, api_hash, string_session):
    with open(SESSION_FILE, "w") as f:
        json.dump({"api_id": api_id, "api_hash": api_hash, "string_session": string_session}, f)


def build_client(api_id, api_hash, session_string=""):
    return TelegramClient(
        StringSession(session_string), api_id, api_hash,
        device_model=DEVICE_MODEL, system_version=SYSTEM_VERSION,
        app_version=APP_VERSION, lang_code=LANG_CODE, system_lang_code=SYSTEM_LANG_CODE
    )


def escape_md(text):
    if not text:
        return "Unknown"
    for ch in ["[", "]", "(", ")", "*", "_", "`"]:
        text = text.replace(ch, f"\\{ch}")
    return text


def is_view_once(message):
    media = message.media
    if isinstance(media, (MessageMediaPhoto, MessageMediaDocument)):
        return bool(getattr(media, "ttl_seconds", None))
    return False


def is_timer(message):
    if is_view_once(message):
        return False
    media = message.media
    if isinstance(media, (MessageMediaPhoto, MessageMediaDocument)):
        return bool(getattr(message, "noforwards", False))
    return False


async def start_userbot(api_id, api_hash, string_session):
    global userbot_client
    client = build_client(api_id, api_hash, string_session)
    await client.start()

    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.dl$"))
    async def dl_handler(event):
        await event.delete()
        if not event.is_reply:
            return
        replied = await event.get_reply_message()
        if not replied or not replied.media:
            return

        sender = await replied.get_sender()
        if sender:
            first = getattr(sender, "first_name", "") or ""
            last = getattr(sender, "last_name", "") or ""
            display = escape_md((f"{first} {last}").strip() or "Unknown")
            mention = f"[{display}](tg://user?id={sender.id})"
        else:
            mention = "Unknown"

        chat = await event.get_chat()
        chat_title = escape_md(getattr(chat, "title", None) or "Private Chat")
        caption = f"\U0001f4e5 **Dari:** {mention}\n\U0001f4ac **Chat:** {chat_title}"

        if is_timer(replied):
            try:
                await client.forward_messages("me", replied)
                await client.send_message("me", caption, parse_mode="markdown")
            except Exception:
                pass
            return

        try:
            media_bytes = await client.download_media(replied.media, bytes)
        except Exception:
            return

        if not media_bytes:
            return

        file_obj = io.BytesIO(media_bytes)
        if isinstance(replied.media, MessageMediaPhoto):
            file_obj.name = "photo.jpg"
        else:
            fname = "media.mp4"
            try:
                for attr in replied.media.document.attributes:
                    if hasattr(attr, "file_name") and attr.file_name:
                        fname = attr.file_name
                        break
            except Exception:
                pass
            file_obj.name = fname

        await client.send_file("me", file=file_obj, caption=caption, parse_mode="markdown")

    userbot_client = client
    print("✅ Client aktif. Balas media view-once/timer dengan .dl")
    asyncio.ensure_future(client.run_until_disconnected())


async def post_init(app):
    data = load_session()
    if data:
        print("🔄 Memuat session tersimpan...")
        await start_userbot(data["api_id"], data["api_hash"], data["string_session"])
        print("✅ Session berhasil dimuat!")


# ─── COMMAND HANDLERS ────────────────────────────────────────────────

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_session()
    status = "✅ *Aktif*" if data else "❌ *Belum diatur*"
    await update.message.reply_text(
        f"👋 *Selamat datang di Downloadinaja!*\n\n"
        f"Status session: {status}\n\n"
        f"Perintah:\n"
        f"/setup — atur session baru\n"
        f"/status — cek status session\n"
        f"/reset — hapus session\n"
        f"/cancel — batalkan proses\n\n"
        f"Setelah setup, balas media view-once/timer dengan `.dl` untuk menyimpannya ke Saved Messages.",
        parse_mode="Markdown"
    )


async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_session()
    if data and userbot_client and userbot_client.is_connected():
        await update.message.reply_text("✅ Session aktif dan berjalan. Kamu bisa pakai `.dl` sekarang.")
    elif data:
        await update.message.reply_text("⚠️ Session tersimpan tapi client belum terhubung. Coba /reset lalu /setup ulang.")
    else:
        await update.message.reply_text("❌ Belum ada session. Gunakan /setup untuk memulai.")


async def cmd_reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global userbot_client
    if userbot_client and userbot_client.is_connected():
        await userbot_client.disconnect()
        userbot_client = None
    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)
    await update.message.reply_text("🗑️ Session berhasil dihapus. Gunakan /setup untuk membuat session baru.")


async def cmd_setup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔢 *Langkah 1/5 — API ID*\n\n"
        "Kirim *API ID* kamu dari https://my.telegram.org\n"
        "_(Contoh: 12345678)_",
        parse_mode="Markdown"
    )
    return API_ID_STEP


async def get_api_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    text = update.message.text.strip()
    if not text.isdigit():
        await update.message.reply_text("❌ API ID harus angka. Coba lagi:")
        return API_ID_STEP
    temp_store[uid] = {"api_id": int(text)}
    await update.message.reply_text(
        "#️⃣ *Langkah 2/5 — API HASH*\n\nKirim *API HASH* kamu:",
        parse_mode="Markdown"
    )
    return API_HASH_STEP


async def get_api_hash(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    temp_store[uid]["api_hash"] = update.message.text.strip()
    await update.message.reply_text(
        "📱 *Langkah 3/5 — Nomor Telepon*\n\nKirim nomor HP beserta kode negara.\n_(Contoh: +628123456789)_",
        parse_mode="Markdown"
    )
    return PHONE_STEP


async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    phone = update.message.text.strip()
    data = temp_store[uid]
    data["phone"] = phone
    try:
        client = build_client(data["api_id"], data["api_hash"])
        await client.connect()
        result = await client.send_code_request(phone)
        data["client"] = client
        data["phone_code_hash"] = result.phone_code_hash
        await update.message.reply_text(
            "✉️ *Langkah 4/5 — Kode OTP*\n\nKode dikirim ke Telegram kamu.\nKirim dengan spasi antar angka.\n_(Contoh: `9 9 9 9 9`)_",
            parse_mode="Markdown"
        )
        return CODE_STEP
    except Exception as e:
        await update.message.reply_text(f"❌ Gagal kirim kode: `{e}`\nCoba /setup lagi.", parse_mode="Markdown")
        return ConversationHandler.END


async def get_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    data = temp_store[uid]
    code = update.message.text.strip().replace(" ", "")
    client: TelegramClient = data["client"]
    try:
        await client.sign_in(phone=data["phone"], code=code, phone_code_hash=data["phone_code_hash"])
        string_session = client.session.save()
        await client.disconnect()
        save_session(data["api_id"], data["api_hash"], string_session)
        temp_store.pop(uid, None)
        await start_userbot(data["api_id"], data["api_hash"], string_session)
        await update.message.reply_text(
            "✅ *Setup berhasil!*\n\nClient sudah aktif. Balas media view-once/timer dengan `.dl` untuk menyimpannya ke Saved Messages.",
            parse_mode="Markdown"
        )
        return ConversationHandler.END
    except SessionPasswordNeededError:
        await update.message.reply_text(
            "🔐 *Langkah 5/5 — Sandi A2F*\n\nAkun kamu pakai verifikasi 2 langkah. Kirim sandinya:",
            parse_mode="Markdown"
        )
        return PASSWORD_STEP
    except (PhoneCodeInvalidError, PhoneCodeExpiredError):
        await update.message.reply_text("❌ Kode OTP tidak valid/kedaluwarsa. Coba /setup lagi.")
        await client.disconnect()
        temp_store.pop(uid, None)
        return ConversationHandler.END
    except Exception as e:
        await update.message.reply_text(f"❌ Error: `{e}`\nCoba /setup lagi.", parse_mode="Markdown")
        await client.disconnect()
        temp_store.pop(uid, None)
        return ConversationHandler.END


async def get_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    data = temp_store[uid]
    client: TelegramClient = data["client"]
    try:
        await client.sign_in(password=update.message.text.strip())
        string_session = client.session.save()
        await client.disconnect()
        save_session(data["api_id"], data["api_hash"], string_session)
        temp_store.pop(uid, None)
        await start_userbot(data["api_id"], data["api_hash"], string_session)
        await update.message.reply_text(
            "✅ *Setup berhasil!*\n\nClient sudah aktif. Balas media view-once/timer dengan `.dl` untuk menyimpannya ke Saved Messages.",
            parse_mode="Markdown"
        )
        return ConversationHandler.END
    except Exception as e:
        await update.message.reply_text(f"❌ Sandi salah: `{e}`\nCoba /setup lagi.", parse_mode="Markdown")
        await client.disconnect()
        temp_store.pop(uid, None)
        return ConversationHandler.END


async def cmd_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    data = temp_store.get(uid, {})
    client = data.get("client")
    if client:
        await client.disconnect()
    temp_store.pop(uid, None)
    await update.message.reply_text("❌ Proses dibatalkan.")
    return ConversationHandler.END


def main():
    app = Application.builder().token(BOT_TOKEN).post_init(post_init).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("setup", cmd_setup)],
        states={
            API_ID_STEP: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_api_id)],
            API_HASH_STEP: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_api_hash)],
            PHONE_STEP: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
            CODE_STEP: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_code)],
            PASSWORD_STEP: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_password)],
        },
        fallbacks=[CommandHandler("cancel", cmd_cancel)],
    )

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("status", cmd_status))
    app.add_handler(CommandHandler("reset", cmd_reset))
    app.add_handler(conv)

    print("🤖 Bot berjalan...")
    app.run_polling()


if __name__ == "__main__":
    main()
