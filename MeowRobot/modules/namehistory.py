#
# Name and Username History Tracker for MeowRoBot
#
from datetime import datetime
from html import escape
from pyrogram import filters, types, ContinuePropagation
from MeowRobot import pbot as bot
from MeowRobot.utils.mongo import db
from MeowRobot.utils.fonts import font

__mod_name__ = "NameHistory"
__module__ = "𝐇ɪꜱᴛᴏʀʏ🕵️"

__help__ = """
*Name & Username History Tracker🕵️*

Track name and username changes for users across Telegram!

*Commands:*
❂ `/namehistory [user/reply]` — View past names and usernames of a user
❂ `/names [user/reply]` — Alias for /namehistory

*Examples:*
`/namehistory` (checks your own history)
Reply to a user with `/namehistory`
`/namehistory 123456789`
`/namehistory @username`
"""

history_db = db.user_name_history


@bot.on_message(filters.all & ~filters.bot, group=101)
async def name_change_watcher(_, m: types.Message):
    if not m.from_user:
        raise ContinuePropagation
    try:
        user = m.from_user
        user_id = user.id
        curr_first = user.first_name or ""
        curr_last = user.last_name or ""
        curr_full = f"{curr_first} {curr_last}".strip()
        curr_user = user.username or ""

        rec = await history_db.find_one({"user_id": user_id})
        now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

        if not rec:
            await history_db.insert_one({
                "user_id": user_id,
                "current_name": curr_full,
                "current_username": curr_user,
                "names": [],
                "usernames": [],
            })
        else:
            updates = {}
            old_name = rec.get("current_name", "")
            old_username = rec.get("current_username", "")

            # If name changed
            if old_name and old_name != curr_full:
                updates.setdefault("$push", {})["names"] = {
                    "name": old_name,
                    "date": now_str,
                }
                updates.setdefault("$set", {})["current_name"] = curr_full
            elif not old_name and curr_full:
                updates.setdefault("$set", {})["current_name"] = curr_full

            # If username changed
            if old_username and old_username != curr_user:
                updates.setdefault("$push", {})["usernames"] = {
                    "username": old_username,
                    "date": now_str,
                }
                updates.setdefault("$set", {})["current_username"] = curr_user
            elif not old_username and curr_user:
                updates.setdefault("$set", {})["current_username"] = curr_user

            if updates:
                await history_db.update_one({"user_id": user_id}, updates)
    except Exception:
        pass

    raise ContinuePropagation


@bot.on_message(filters.command(["namehistory", "names", "history"]))
async def name_history_handler(_, m: types.Message):
    target_user = None

    if m.reply_to_message and m.reply_to_message.from_user:
        target_user = m.reply_to_message.from_user
    elif len(m.command) > 1:
        arg = m.command[1].strip()
        try:
            if arg.isdigit():
                target_user = await bot.get_users(int(arg))
            else:
                target_user = await bot.get_users(arg)
        except Exception:
            return await m.reply_text(font(f"❌ User `{arg}` not found or invalid."))
    else:
        target_user = m.from_user

    if not target_user:
        return await m.reply_text(font("❌ Could not determine target user."))

    user_id = target_user.id
    first_name = target_user.first_name or ""
    last_name = target_user.last_name or ""
    full_name = escape(f"{first_name} {last_name}".strip())
    username = f"@{target_user.username}" if target_user.username else "None"

    rec = await history_db.find_one({"user_id": user_id})

    text = f"🕵️ <b>Name & Username Audit Trail</b>\n\n"
    text += f"👤 <b>User:</b> <a href='tg://user?id={user_id}'>{full_name}</a>\n"
    text += f"🆔 <b>User ID:</b> <code>{user_id}</code>\n"
    text += f"🌐 <b>Current Username:</b> {username}\n\n"

    if not rec or (not rec.get("names") and not rec.get("usernames")):
        text += "ℹ️ <i>No past name or username changes recorded for this user yet.</i>\n"
    else:
        past_names = rec.get("names", [])
        if past_names:
            text += "📝 <b>Past Names:</b>\n"
            for n in past_names[-10:]:
                text += f"• <code>{escape(n.get('name', ''))}</code> (<i>{n.get('date', '')}</i>)\n"
            text += "\n"
        else:
            text += "📝 <b>Past Names:</b> <i>No changes recorded</i>\n\n"

        past_usernames = rec.get("usernames", [])
        if past_usernames:
            text += "🌐 <b>Past Usernames:</b>\n"
            for u in past_usernames[-10:]:
                u_name = u.get("username", "")
                text += f"• <code>@{escape(u_name)}</code> (<i>{u.get('date', '')}</i>)\n"
        else:
            text += "🌐 <b>Past Usernames:</b> <i>No changes recorded</i>\n"

    bot_name = bot.me.username if bot.me else "MeowRoBot"
    text += f"\n⚡ <b>Audited by @{bot_name}</b>"

    await m.reply_text(text, disable_web_page_preview=True)
