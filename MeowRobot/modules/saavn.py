#
# JioSaavn High Quality 320kbps Music Downloader for MeowRoBot
#
import os
import html
import base64
import aiohttp
from Crypto.Cipher import DES
from pyrogram import filters, types

from MeowRobot import pbot as bot
from MeowRobot.utils.fonts import font

__mod_name__ = "JioSaavn"
__module__ = "𝐉ɪᴏ𝐒ᴀᴀᴠɴ🎵"

__help__ = """
*JioSaavn Music Downloader🎵*

Download high-quality 320kbps Bollywood & Indian songs directly with full album cover and metadata!

*Commands:*
❂ `/saavn <song name>` — Download 320kbps audio from JioSaavn
❂ `/jiosaavn <song name>` — Same as /saavn

*Example:*
`/saavn Kesariya`
`/saavn Tum Hi Ho`
"""

DES_KEY = b"38346591"


def decrypt_saavn_url(enc_url: str) -> str:
    cipher = DES.new(DES_KEY, DES.MODE_ECB)
    dec = cipher.decrypt(base64.b64decode(enc_url))
    pad = dec[-1]
    return dec[:-pad].decode("utf-8", errors="ignore").strip()


@bot.on_message(filters.command(["saavn", "jiosaavn"]) & ~filters.forwarded)
async def saavn_handler(_, m: types.Message):
    if len(m.command) < 2:
        return await m.reply_text(
            font("❌ Please provide a song name to search on JioSaavn.\nExample: `/saavn Kesariya`")
        )

    query = m.text.split(maxsplit=1)[1].strip()
    status = await m.reply_text(font(f"🔍 Searching JioSaavn for `{query}`..."))

    audio_file = None
    thumb_file = None

    try:
        timeout = aiohttp.ClientTimeout(total=30)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            search_url = (
                f"https://www.jiosaavn.com/api.php?__call=autocomplete.get"
                f"&_format=json&_marker=0&cc=in&includeMetaTags=1&query={query}"
            )
            async with session.get(search_url) as resp:
                data = await resp.json(content_type=None)
                songs = data.get("songs", {}).get("data", [])
                if not songs:
                    return await status.edit_text(font(f"❌ No songs found for `{query}` on JioSaavn."))

                first_song = songs[0]
                song_id = first_song.get("id")

            # Fetch detailed song metadata
            detail_url = (
                f"https://www.jiosaavn.com/api.php?__call=song.getDetails"
                f"&cc=in&_marker=0%3F_marker%3D0&_format=json&pids={song_id}"
            )
            async with session.get(detail_url) as resp:
                detail_data = await resp.json(content_type=None)
                info = detail_data.get(song_id, {})
                enc_url = info.get("encrypted_media_url")
                if not enc_url:
                    return await status.edit_text(font("❌ Failed to retrieve media link for this song."))

                raw_url = decrypt_saavn_url(enc_url)
                # Try 320kbps first
                stream_url = raw_url.replace("_96.mp4", "_320.mp4").replace("_160.mp4", "_320.mp4")

                title = html.unescape(info.get("song", first_song.get("title", query)))
                singers = html.unescape(info.get("singers") or info.get("primary_artists", "Unknown Artist"))
                album = html.unescape(info.get("album", "JioSaavn Single"))
                duration = int(info.get("duration", 0)) if str(info.get("duration", "")).isdigit() else 0
                image_url = info.get("image", "").replace("150x150", "500x500")

            await status.edit_text(font(f"⚡ Downloading `{title}` (320kbps)..."))

            # Download audio file
            audio_file = f"saavn_{m.chat.id}_{m.id}.m4a"
            async with session.get(stream_url) as dl_resp:
                if dl_resp.status != 200:
                    # Fallback to standard 160/96kbps
                    stream_url = raw_url.replace("_96.mp4", "_160.mp4")
                    async with session.get(stream_url) as fb_resp:
                        if fb_resp.status != 200:
                            stream_url = raw_url
                            async with session.get(stream_url) as def_resp:
                                with open(audio_file, "wb") as f:
                                    f.write(await def_resp.read())
                        else:
                            with open(audio_file, "wb") as f:
                                f.write(await fb_resp.read())
                else:
                    with open(audio_file, "wb") as f:
                        f.write(await dl_resp.read())

            # Download thumbnail if available
            if image_url:
                try:
                    thumb_file = f"thumb_{m.chat.id}_{m.id}.jpg"
                    async with session.get(image_url) as img_resp:
                        if img_resp.status == 200:
                            with open(thumb_file, "wb") as f:
                                f.write(await img_resp.read())
                        else:
                            thumb_file = None
                except Exception:
                    thumb_file = None

        bot_name = bot.me.username if bot.me else "MeowRoBot"
        caption = (
            f"🎵 **Title:** `{title}`\n"
            f"🎙 **Artist:** `{singers}`\n"
            f"💿 **Album:** `{album}`\n\n"
            f"**Downloaded by @{bot_name} ⚡**"
        )

        await m.reply_audio(
            audio=audio_file,
            caption=caption,
            title=title,
            performer=singers,
            duration=duration,
            thumb=thumb_file,
        )
        await status.delete()

    except Exception as e:
        await status.edit_text(f"❌ **Error downloading song:** {e}")

    finally:
        if audio_file and os.path.isfile(audio_file):
            try:
                os.remove(audio_file)
            except Exception:
                pass
        if thumb_file and os.path.isfile(thumb_file):
            try:
                os.remove(thumb_file)
            except Exception:
                pass
