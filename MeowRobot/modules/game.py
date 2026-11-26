import random
import asyncio
from datetime import datetime, timedelta, date
from pyrogram import filters, types, enums

from MeowRobot import pbot as bot, DRAGONS as DEV_LIST
from MeowRobot.utils.fonts import font
from MeowRobot.utils.mongo import db

__mod_name__ = "Games"
__module__ = "𝐆ᴀᴍᴇs🎮"

__help__ = """
❂ *Game Module* — Have fun and compete with your friends using mini-games in your Telegram chat.

❂ *Commands*:
❂ `/steal` — Try to steal coins from other users.  
❂ `/bowl` — Play a bowling mini-game.  
❂ `/dart` — Test your aim with darts.  
❂ `/dice` — Roll a dice and see what luck brings you.  
❂ `/gamble <amount>` — Gamble coins for a chance to win big.  
❂ `/balance` — Check your current coin balance.  
❂ `/richlist` — See the leaderboard of richest users.  
❂ `/domain` — Alternative command for steal heist.  
❂ `/setcash <user_id> <amount>` — Admin command to set user balance.  

❂ *Features*:
❂ Earn coins, gamble, and climb the leaderboard.  
❂ Interactive mini-games to challenge friends.  
❂ Track balances and stats for fun competitions.  
"""

def get_full_name(user) -> str:
    if not user:
        return "Unknown"
    return f"{user.first_name} {user.last_name or ''}".strip()


# Database collections
gamedb = db.game_users
stealdb = db.game_steals

async def get_cash(user_id: int) -> int:
    user = await gamedb.find_one({"user_id": user_id})
    return int(user.get("cash", 0)) if user else 0

async def update_cash(user_id: int, amount: int) -> bool:
    await gamedb.update_one(
        {"user_id": user_id},
        {"$inc": {"cash": int(amount)}},
        upsert=True
    )
    return True

async def update_name(user_id: int, name: str):
    await gamedb.update_one(
        {"user_id": user_id},
        {"$set": {"name": name}},
        upsert=True
    )

async def get_steal_date(user_id: int, target_id: int):
    doc = await stealdb.find_one({"user_id": user_id, "target_id": target_id})
    return doc.get("date") if doc else None

async def update_steal_date(user_id: int, target_id: int, date_val):
    await stealdb.update_one(
        {"user_id": user_id, "target_id": target_id},
        {"$set": {"date": date_val}},
        upsert=True
    )

async def get_top_users(limit: int = 10):
    cursor = gamedb.find().sort("cash", -1).limit(limit)
    return await cursor.to_list(length=limit)


# Flood control
dice_users = {}
dart_users = {}
bowl_users = {}
FLOOD_MAX = 10  # in minutes

# Images
TRY_LATER_IMG = "https://files.catbox.moe/yjiess.jpg"
GOOD_LUCK_IMG = "https://files.catbox.moe/2y8fnb.jpg"
BAD_LUCK_IMG = "https://files.catbox.moe/4cyx4f.jpg"
SERIOUS_IMG = "https://files.catbox.moe/ee8bky.jpg"


# Remove user after delay
async def remove_user_after_delay(user_id, data):
    await asyncio.sleep(FLOOD_MAX * 60)
    data.pop(user_id, None)


# Admin command: set user cash
@bot.on_message(filters.command("setcash") & filters.user(DEV_LIST))
async def _setUserCash(_, m: types.Message):
    try:
        user_id = int(m.text.split()[1])
        cash = int(m.text.split()[2])
        if await update_cash(user_id, cash):
            await m.reply(font("✅ Cash added to account!"))
    except Exception as e:
        await m.reply(f"❌ ERROR: {e}")


# Richlist
@bot.on_message(filters.command("richlist"))
async def _richList(_, m: types.Message):
    users_list = await get_top_users()
    if not users_list:
        return await m.reply(font("**Yo, fam!** No top users in sight. 😅"))

    text = "💸💸 **Rich Players flexin' in the groups... 💸💸**\n\n"

    for roll, user in enumerate(users_list, start=1):
        if user.get("cash", 0) == 0:
            continue

        user_id = user.get("user_id")
        user_name = user.get("name")
        if not user_name:
            try:
                telegram_user = await bot.get_users(user_id)
                user_name = get_full_name(telegram_user)
                await update_name(user_id, user_name)
            except Exception:
                user_name = "Unknown"

        mention = f"[{user_name}](tg://user?id={user_id})"
        text += f"{roll}. {mention} — {user['cash']} 💸\n"

    text += "\n**Think you can outshine me? Bring it on! 😼**"
    await m.reply_photo("https://files.catbox.moe/562cjr.jpg", caption=text, parse_mode=enums.ParseMode.MARKDOWN)


# Balance check
@bot.on_message(filters.command("balance") & ~filters.forwarded)
async def _checkBalance(_, m: types.Message):
    user = m.from_user
    cash = await get_cash(user.id)
    if cash == 0:
        return await m.reply("*Bro* You are too poor, try making some money otherwise you can't live in the world! 🥴")
    await update_name(user.id, get_full_name(user))
    await m.reply_photo(TRY_LATER_IMG, caption=f"**Yo, {get_full_name(user)}! Your balance is a whopping {cash} cash!** 💸💸")


# Steal command
@bot.on_message(filters.command(["domain", "steal"]))
async def _stealCash(_, m: types.Message):
    user = m.from_user
    reply = m.reply_to_message
    if not reply:
        return await m.reply(font("You need to reply to a fellow sorcerer, **bro** 😖"))
    if reply.from_user.is_bot or reply.from_user.id == user.id:
        return

    user_cash = await get_cash(user.id)
    reply_user = reply.from_user
    today = date.today().day

    prev_steal = await get_steal_date(user.id, reply_user.id)
    if prev_steal and today == prev_steal:
        return await m.reply("You've already pulled a heist today! Try again tomorrow 😈")

    if user_cash < 1000:
        return await m.reply(font("To pull off a heist, you need at least 1000 cash 💸."))

    reply_cash = await get_cash(reply_user.id)
    if reply_cash < 1000:
        return await m.reply(font("Lol! Not enough cursed energy to steal from someone! They need at least 1000 cash 💸"))

    bot_name = bot.me.username if bot.me else "MeowRoBot"
    msg = await m.reply(font(f"@{bot_name} cloths open! ..."))
    await update_steal_date(user.id, reply_user.id, today)
    await asyncio.sleep(2)

    steal_percentage = random.randint(1, 60)
    success = random.choice([True, False])

    if not success:
        await msg.edit("😱 Oh no! You don't stand a chance against them today.")
    else:
        amount = int((steal_percentage / 100) * reply_cash)
        await update_cash(user.id, amount)
        await update_cash(reply_user.id, -amount)
        await msg.edit(f"🤑 You just snagged {amount} cash 💸💸 ({steal_percentage}%) from {get_full_name(reply_user)}! 😼")


# Gamble command
@bot.on_message(filters.command(["gamble"]) & ~filters.forwarded)
async def _gamble(_, m: types.Message):
    user = m.from_user
    cash = await get_cash(user.id)
    if cash == 0:
        return await m.reply("😂 You're broke, *sorcerer*. Go earn something.")

    if len(m.command) < 2 or not m.command[1].isdigit():
        return await m.reply(font("🙄 Enter a valid amount.\nExample: /gamble 1000"))

    gamble = int(m.command[1])
    if gamble > cash:
        return await m.reply("😂 You don't have enough cash to gamble.")

    results = [2, -1.2, 0, 1.2, 0, -1.5, 1.5, 0, 0, 2.1, 1.3, 1.4, -1.2]
    multiplier = random.choice(results)

    if multiplier < 0:
        loss = int(gamble * abs(multiplier))
        await update_cash(user.id, -loss)
        return await m.reply_photo(SERIOUS_IMG, caption=f"🤧 You lost {loss} 💸 to a curse!")
    elif multiplier > 0:
        win = int(gamble * multiplier)
        await update_cash(user.id, win)
        return await m.reply_photo(GOOD_LUCK_IMG, caption=f"🔥 You earned {win} Cash! 💸")
    else:
        await update_cash(user.id, -gamble)
        return await m.reply_photo(BAD_LUCK_IMG, caption=f"😭 You lost {gamble} Cash. Try again!")


# Score + reward game handler
async def handle_dice_game(user, m, emoji, user_dict, rewards):
    if user.id in user_dict:
        remaining = (user_dict[user.id] - datetime.now()).total_seconds() / 60
        return await m.reply_photo(
            TRY_LATER_IMG,
            caption=f"🥲 Don't spam. Try again after {remaining:.2f} minutes ⏳"
        )

    user_dict[user.id] = datetime.now() + timedelta(minutes=FLOOD_MAX)

    msg_dice = await bot.send_dice(
        chat_id=m.chat.id,
        emoji=emoji,
        reply_to_message_id=m.id
    )
    value = msg_dice.dice.value
    reward = rewards.get(value, 0)

    caption = f"🎲 **{get_full_name(user)} scored** `{value}`!\n"
    if reward > 0:
        await update_cash(user.id, reward)
        caption += f"💰 Earned: `{reward}` Cash 💸"
        image = GOOD_LUCK_IMG
    else:
        caption += "😢 No reward this time. Keep trying!"
        image = SERIOUS_IMG

    await msg_dice.reply_photo(image, caption=caption)
    asyncio.create_task(remove_user_after_delay(user.id, user_dict))


# Rewards
DICE_REWARDS = {1: 1000, 2: 1500, 3: 2500, 4: 3500, 5: 5000, 6: 10000}
DART_REWARDS = {1: 500, 2: 1000, 3: 2000, 4: 3000, 5: 6000, 6: 10000}
BOWL_REWARDS = {1: 700, 2: 1200, 3: 2200, 4: 3200, 5: 5500, 6: 9000}


# Dice command
@bot.on_message(filters.command("dice") & ~filters.forwarded)
async def _roll_dice(_, m: types.Message):
    await handle_dice_game(m.from_user, m, "🎲", dice_users, DICE_REWARDS)


# Dart command
@bot.on_message(filters.command("dart") & ~filters.forwarded)
async def _roll_dart(_, m: types.Message):
    await handle_dice_game(m.from_user, m, "🎯", dart_users, DART_REWARDS)


# Bowl command
@bot.on_message(filters.command("bowl") & ~filters.forwarded)
async def _roll_bowl(_, m: types.Message):
    await handle_dice_game(m.from_user, m, "🎳", bowl_users, BOWL_REWARDS)
