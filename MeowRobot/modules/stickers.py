#
# Copyright (C) 2021-2022 by TheAloneteam@Github, < https://github.com/TheAloneTeam >.
# This file is part of < https://github.com/TheAloneTeam/MeowRobot > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/TheAloneTeam/MeowRobot/blob/master/LICENSE >
#
# All rights reserved.

import math
import os
import asyncio
from html import escape
from io import BytesIO

import requests
from bs4 import BeautifulSoup as bs
from PIL import Image
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputSticker,
    Update,
)
from telegram.constants import ParseMode, StickerFormat
from telegram.helpers import mention_html
from telegram.error import BadRequest
from telegram.ext import ContextTypes

from MeowRobot import application
from MeowRobot.modules.disable import DisableAbleCommandHandler

combot_stickers_url = "https://combot.org/telegram/stickers?q="


async def sticker_count(bot, pname: str) -> int:
    try:
        stickerset = await bot.get_sticker_set(pname)
        return len(stickerset.stickers)
    except BadRequest:
        return 0


async def stickerid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    if msg.reply_to_message and msg.reply_to_message.sticker:
        await update.effective_message.reply_text(
            "Hey "
            + f"{mention_html(msg.from_user.id, msg.from_user.first_name)}"
            + ", The sticker id you are replying is :\n <code>"
            + escape(msg.reply_to_message.sticker.file_id)
            + "</code>",
            disable_web_page_preview=True,
            parse_mode=ParseMode.HTML,
        )
    else:
        await update.effective_message.reply_text(
            "Hello "
            + f"{mention_html(msg.from_user.id, msg.from_user.first_name)}"
            + ", Please reply to sticker message to get id sticker",
            disable_web_page_preview=True,
            parse_mode=ParseMode.HTML,
        )


async def cb_sticker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    split = msg.text.split(" ", 1)
    if len(split) == 1:
        await msg.reply_text("Provide some name to search for pack.")
        return

    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(None, requests.get, combot_stickers_url + split[1])
    text = response.text
    soup = bs(text, "lxml")
    results = soup.find_all("a", {"class": "sticker-pack__btn"})
    titles = soup.find_all("div", "sticker-pack__title")
    if not results:
        await msg.reply_text("No results found :(.")
        return
    reply = f"Stickers for *{split[1]}*:"
    for result, title in zip(results, titles):
        link = result["href"]
        reply += f"\n• [{title.get_text()}]({link})"
    await msg.reply_text(reply, parse_mode=ParseMode.MARKDOWN)


async def getsticker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    msg = update.effective_message
    if msg.reply_to_message and msg.reply_to_message.sticker:
        file_id = msg.reply_to_message.sticker.file_id
        is_anim = msg.reply_to_message.sticker.is_animated
        is_video = msg.reply_to_message.sticker.is_video

        sticker_file = await bot.get_file(file_id)
        sticker_data = BytesIO()
        await sticker_file.download_to_memory(out=sticker_data)
        sticker_data.seek(0)

        if is_anim:
             filename = "animated_sticker.tgs"
        elif is_video:
             filename = "video_sticker.webm"
        else:
             filename = "sticker.png"

        await bot.send_document(
            update.effective_chat.id,
            document=sticker_data,
            filename=filename,
        )
    else:
        await update.effective_message.reply_text(
            "Please reply to a sticker for me to upload its file."
        )


async def kang(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    user = update.effective_user
    args = context.args
    packnum = 0
    packname = "a" + str(user.id) + "_by_" + context.bot.username
    packname_found = 0
    max_stickers = 120

    while packname_found == 0:
        count = await sticker_count(context.bot, packname)
        if count >= max_stickers:
            packnum += 1
            packname = (
                "a"
                + str(packnum)
                + "_"
                + str(user.id)
                + "_by_"
                + context.bot.username
            )
        else:
            packname_found = 1

    is_animated = False
    is_video = False
    file_id = ""

    if msg.reply_to_message:
        if msg.reply_to_message.sticker:
            if msg.reply_to_message.sticker.is_animated:
                is_animated = True
            elif msg.reply_to_message.sticker.is_video:
                is_video = True
            file_id = msg.reply_to_message.sticker.file_id

        elif msg.reply_to_message.photo:
            file_id = msg.reply_to_message.photo[-1].file_id
        elif msg.reply_to_message.document:
            file_id = msg.reply_to_message.document.file_id
        else:
            await msg.reply_text("Yea, I can't kang that.")
            return

        kang_file = await context.bot.get_file(file_id)
        if is_animated:
            extension = "tgs"
        elif is_video:
            extension = "webm"
        else:
            extension = "png"

        sticker_filename = f"kang_{user.id}_{msg.message_id}.{extension}"
        await kang_file.download_to_drive(sticker_filename)

        if args:
            sticker_emoji = str(args[0])
        elif msg.reply_to_message.sticker and msg.reply_to_message.sticker.emoji:
            sticker_emoji = msg.reply_to_message.sticker.emoji
        else:
            sticker_emoji = "🤔"

        try:
            if not is_animated and not is_video:
                try:
                    im = Image.open(sticker_filename)
                    maxsize = (512, 512)
                    if (im.width and im.height) < 512:
                        size1 = im.width
                        size2 = im.height
                        if im.width > im.height:
                            scale = 512 / size1
                            size1new = 512
                            size2new = size2 * scale
                        else:
                            scale = 512 / size2
                            size1new = size1 * scale
                            size2new = 512
                        size1new = math.floor(size1new)
                        size2new = math.floor(size2new)
                        sizenew = (size1new, size2new)
                        im = im.resize(sizenew)
                    else:
                        im.thumbnail(maxsize)
                    im.save(sticker_filename, "PNG")

                    with open(sticker_filename, "rb") as st_file:
                        try:
                            await context.bot.add_sticker_to_set(
                                user_id=user.id,
                                name=packname,
                                sticker=InputSticker(
                                    sticker=st_file,
                                    emoji_list=[sticker_emoji],
                                    format=StickerFormat.STATIC,
                                ),
                            )
                        except BadRequest as e:
                            if e.message == "Stickerset_invalid":
                                st_file.seek(0)
                                await makepack_internal(
                                    update,
                                    context,
                                    msg,
                                    user,
                                    sticker_emoji,
                                    packname,
                                    packnum,
                                    sticker=st_file,
                                )
                            else:
                                raise e

                    await msg.reply_text(
                        f"Sticker successfully added to [pack](t.me/addstickers/{packname})"
                        + f"\nEmoji is: {sticker_emoji}",
                        disable_web_page_preview=True,
                        parse_mode=ParseMode.MARKDOWN,
                    )

                except Exception as e:
                    await msg.reply_text(f"Error: {e}")
                    return

            elif is_animated:
                try:
                    with open(sticker_filename, "rb") as st_file:
                        try:
                            await context.bot.add_sticker_to_set(
                                user_id=user.id,
                                name=packname,
                                sticker=InputSticker(
                                    sticker=st_file,
                                    emoji_list=[sticker_emoji],
                                    format=StickerFormat.ANIMATED,
                                ),
                            )
                        except BadRequest as e:
                            if e.message == "Stickerset_invalid":
                                st_file.seek(0)
                                await makepack_internal(
                                    update,
                                    context,
                                    msg,
                                    user,
                                    sticker_emoji,
                                    packname,
                                    packnum,
                                    sticker=st_file,
                                    is_animated=True,
                                )
                            else:
                                raise e
                    await msg.reply_text(
                        f"Sticker successfully added to [pack](t.me/addstickers/{packname})"
                        + f"\nEmoji is: {sticker_emoji}",
                        disable_web_page_preview=True,
                        parse_mode=ParseMode.MARKDOWN,
                    )
                except Exception as e:
                    await msg.reply_text(f"Error: {e}")
                    return

            elif is_video:
                try:
                    with open(sticker_filename, "rb") as st_file:
                        try:
                            await context.bot.add_sticker_to_set(
                                user_id=user.id,
                                name=packname,
                                sticker=InputSticker(
                                    sticker=st_file,
                                    emoji_list=[sticker_emoji],
                                    format=StickerFormat.VIDEO,
                                ),
                            )
                        except BadRequest as e:
                            if e.message == "Stickerset_invalid":
                                st_file.seek(0)
                                await makepack_internal(
                                    update,
                                    context,
                                    msg,
                                    user,
                                    sticker_emoji,
                                    packname,
                                    packnum,
                                    sticker=st_file,
                                    is_video=True,
                                )
                            else:
                                raise e
                    await msg.reply_text(
                        f"Sticker successfully added to [pack](t.me/addstickers/{packname})"
                        + f"\nEmoji is: {sticker_emoji}",
                        disable_web_page_preview=True,
                        parse_mode=ParseMode.MARKDOWN,
                    )
                except Exception as e:
                    await msg.reply_text(f"Error: {e}")
                    return
        finally:
            if os.path.isfile(sticker_filename):
                try:
                    os.remove(sticker_filename)
                except Exception:
                    pass


async def makepack_internal(
    update,
    context,
    msg,
    user,
    emoji,
    packname,
    packnum,
    sticker=None,
    is_animated=False,
    is_video=False,
):
    name = user.first_name[:50]
    try:
        extra_version = f" {packnum}" if packnum > 0 else ""
        if is_animated:
            sticker_format = StickerFormat.ANIMATED
            title = f"{name}s animated kang pack{extra_version}"
        elif is_video:
            sticker_format = StickerFormat.VIDEO
            title = f"{name}s video kang pack{extra_version}"
        else:
            sticker_format = StickerFormat.STATIC
            title = f"{name}s kang pack{extra_version}"

        await context.bot.create_new_sticker_set(
            user_id=user.id,
            name=packname,
            title=title,
            stickers=[
                InputSticker(
                    sticker=sticker,
                    emoji_list=[emoji],
                    format=sticker_format,
                )
            ],
        )

        await msg.reply_text(
            "Sticker pack successfully created. Get it [here](t.me/addstickers/%s)"
            % packname,
            disable_web_page_preview=True,
            parse_mode=ParseMode.MARKDOWN,
        )

    except BadRequest as e:
        if e.message == "Sticker set name is already occupied":
            await msg.reply_text(
                "Your pack can be found [here](t.me/addstickers/%s)" % packname,
                disable_web_page_preview=True,
                parse_mode=ParseMode.MARKDOWN,
            )
        elif e.message in ("Peer_id_invalid", "bot was blocked by the user"):
            await msg.reply_text(
                "Contact me in PM first.",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="Start", url=f"t.me/{context.bot.username}"
                            )
                        ]
                    ]
                ),
            )
        else:
            await msg.reply_text(f"Failed to create sticker pack: {e.message}")


__help__ = """
  /stickerid*:* reply to a sticker to me to tell you its file ID.
  /getsticker*:* reply to a sticker to me to upload its raw PNG file.
  /kang or /pkang*:* reply to a sticker or photo to add it to your pack.
  /stickers*:* Find stickers for given term on combot sticker catalogue
"""

__mod_name__ = "Sᴛɪᴄᴋᴇʀ"

STICKERID_HANDLER = DisableAbleCommandHandler("stickerid", stickerid)
GETSTICKER_HANDLER = DisableAbleCommandHandler("getsticker", getsticker)
KANG_HANDLER = DisableAbleCommandHandler(["kang", "pkang"], kang, admin_ok=True)
STICKERS_HANDLER = DisableAbleCommandHandler("stickers", cb_sticker)

application.add_handler(STICKERS_HANDLER)
application.add_handler(STICKERID_HANDLER)
application.add_handler(GETSTICKER_HANDLER)
application.add_handler(KANG_HANDLER)
