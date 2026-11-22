#
# Group Activity Stats & Leaderboard Module for MeowRoBot
#
from html import escape
from pyrogram import filters, types, ContinuePropagation
from MeowRobot import pbot as bot
from MeowRobot.utils.mongo import db
from MeowRobot.utils.fonts import font

__mod_name__ = "ChatStats"
__module__ = "𝐒ᴛᴀᴛꜱ📊"

__help__ = """
*Group Activity & Leaderboard📊*

Track active members and message statistics in your group!

*Commands:*
❂ `/chatstats` or `/topmembers` — Display top 10 most active members
❂ `/mystats` — Check your own message count and rank in the group
❂ `/resetstats` — Reset activity statistics for this chat (Admin only)
"""

stats_db = db.chat_activity


@bot.on_message(filters.group & ~filters.bot, group=100)
async def chat_activity_tracker(_, m: types.Message):
    if not m.from_user or not m.chat:
        raise ContinuePropagation
    try:
        name = (m.from_user.first_name or "User")[:30]
        username = m.from_user.username or ""
        await stats_db.update_one(
            {"chat_id": m.chat.id, "user_id": m.from_user.id},
            {
                "$inc": {"messages": 1},
                "$set": {"name": name, "username": username},
            },
            upsert=True,
        )
    except Exception:
        pass

    raise ContinuePropagation


@bot.on_message(filters.command(["chatstats", "topmembers", "leaderboard"]) & filters.group)
async def chatstats_handler(_, m: types.Message):
    chat_id = m.chat.id
    status = await m.reply_text(font("📊 Calculating activity leaderboard..."))

    try:
        cursor = stats_db.find({"chat_id": chat_id}).sort("messages", -1).limit(10)
        top_list = await cursor.to_list(length=10)

        if not top_list:
            return await status.edit_text(font("ℹ️ No message activity recorded in this group yet."))

        medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
        text = f"📊 **Activity Leaderboard for {escape(m.chat.title)}**\n\n"

        for i, user in enumerate(top_list):
            badge = medals[i] if i < len(medals) else f"`{i+1}.`"
            user_name = escape(user.get("name", "User"))
            user_id = user.get("user_id")
            count = user.get("messages", 0)
            text += f"{badge} <a href='tg://user?id={user_id}'>{user_name}</a> ➔ <b>{count:,}</b> msgs\n"

        total_cursor = stats_db.aggregate([
            {"$match": {"chat_id": chat_id}},
            {"$group": {"_id": None, "total": {"$sum": "$messages"}}}
        ])
        total_list = await total_cursor.to_list(length=1)
        total_msgs = total_list[0]["total"] if total_list else 0

        text += f"\n💬 **Total Recorded Messages:** <code>{total_msgs:,}</code>"
        bot_name = bot.me.username if bot.me else "MeowRoBot"
        text += f"\n⚡ **Powered by @{bot_name}**"

        await status.edit_text(text, disable_web_page_preview=True)

    except Exception as e:
        await status.edit_text(f"❌ **Error generating chat stats:** {e}")


@bot.on_message(filters.command(["mystats"]) & filters.group)
async def mystats_handler(_, m: types.Message):
    if not m.from_user:
        return
    chat_id = m.chat.id
    user_id = m.from_user.id

    try:
        user_record = await stats_db.find_one({"chat_id": chat_id, "user_id": user_id})
        msg_count = user_record.get("messages", 0) if user_record else 0

        # Calculate rank
        higher_count = await stats_db.count_documents(
            {"chat_id": chat_id, "messages": {"$gt": msg_count}}
        )
        rank = higher_count + 1

        text = (
            f"📈 **Your Activity in {escape(m.chat.title)}**\n\n"
            f"👤 **User:** <a href='tg://user?id={user_id}'>{escape(m.from_user.first_name)}</a>\n"
            f"💬 **Messages Sent:** <code>{msg_count:,}</code>\n"
            f"🏆 **Current Rank:** <code>#{rank}</code>\n"
        )
        await m.reply_text(text, disable_web_page_preview=True)

    except Exception as e:
        await m.reply_text(f"❌ **Error:** {e}")


@bot.on_message(filters.command(["resetstats"]) & filters.group)
async def resetstats_handler(_, m: types.Message):
    # Check if user is admin or owner
    member = await m.chat.get_member(m.from_user.id)
    if not (member.status in [types.enums.ChatMemberStatus.ADMINISTRATOR, types.enums.ChatMemberStatus.OWNER]):
        return await m.reply_text(font("❌ Only administrators can reset group activity stats."))

    await stats_db.delete_many({"chat_id": m.chat.id})
    await m.reply_text(font("✅ Group activity statistics have been successfully reset!"))
