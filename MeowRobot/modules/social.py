import os
import glob
import asyncio
import aiohttp
from bs4 import BeautifulSoup
import yt_dlp
from pyrogram import filters, types

from MeowRobot import pbot as bot
from MeowRobot.utils.fonts import font

__mod_name__ = "Social"
__module__ = "𝐒ᴏᴄɪᴀʟ🌐"

__help__ = """
*Social Downloader🌐*

*Description:*  
Download media from popular platforms like Instagram, Twitter/X, TikTok, and Pinterest directly through the bot.

*Commands:*  
❂ `/ig <url>` or `/insta <url>` — Download Instagram Reels or Posts  
❂ `/tw <url>` or `/twitter <url>` or `/x <url>` — Download Twitter / X Video  
❂ `/tt <url>` or `/tiktok <url>` — Download TikTok Video  
❂ `/pinterest <url>` or `/pin <query>` — Download Pinterest image or video  

*Examples:*  
`/ig https://www.instagram.com/reel/C8xxx/`  
`/tw https://x.com/user/status/12345678`  
`/tt https://www.tiktok.com/@user/video/12345678`  
`/pin cute anime wallpaper`
"""

async def instagram_download(link: str) -> list:
    results = []
    headers = {
        'origin': 'https://saveinsta.app',
        'referer': 'https://saveinsta.app/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    data = {'q': link, 'vt': 'home'}
    url = 'https://v3.saveinsta.app/api/ajaxSearch'

    try:
        timeout = aiohttp.ClientTimeout(total=20)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(url, data=data, headers=headers) as resp:
                if resp.status == 200:
                    res_json = await resp.json()
                    html_data = res_json.get('data', '')
                    if html_data:
                        soup = BeautifulSoup(html_data, 'html.parser')
                        for item in soup.find_all('div', class_='download-items__btn'):
                            a_tag = item.find('a')
                            if a_tag and a_tag.get('href'):
                                results.append(a_tag['href'])
    except Exception:
        pass
    return results


def download_ytdl_video(url: str, output_template: str) -> str:
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': output_template,
        'quiet': True,
        'no_warnings': True,
        'merge_output_format': 'mp4',
        'max_filesize': 50 * 1024 * 1024,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info).rsplit('.', 1)[0] + '.mp4'


@bot.on_message(filters.command(["ig", "insta", "igdl"]) & ~filters.forwarded)
async def insta_handler(_, m: types.Message):
    if len(m.command) < 2:
        return await m.reply_text(font("❌ Please provide an Instagram post or reel URL.\nExample: `/ig https://instagram.com/reel/...`"))

    url = m.command[1].strip()
    loading = await m.reply_text(font("⏳ Fetching Instagram media..."))

    try:
        media_urls = await instagram_download(url)
        if not media_urls:
            return await loading.edit_text(font("❌ Could not download media. Ensure the account is public or link is valid."))

        target_url = media_urls[0]
        bot_name = bot.me.username if bot.me else "MeowRoBot"

        if ".mp4" in target_url or "video" in target_url:
            await m.reply_video(target_url, caption=f"**Downloaded by @{bot_name} ⚡**")
        else:
            await m.reply_photo(target_url, caption=f"**Downloaded by @{bot_name} ⚡**")
        await loading.delete()
    except Exception as e:
        await loading.edit_text(f"❌ **Error:** {e}")


@bot.on_message(filters.command(["tw", "twitter", "x"]) & ~filters.forwarded)
async def twitter_handler(_, m: types.Message):
    if len(m.command) < 2:
        return await m.reply_text(font("❌ Please provide a Twitter/X URL.\nExample: `/tw https://x.com/...`"))

    url = m.command[1].strip()
    loading = await m.reply_text(font("⏳ Downloading Twitter/X video..."))
    out_tmpl = f"tw_{m.chat.id}_{m.id}.%(ext)s"
    final_video = None

    try:
        loop = asyncio.get_event_loop()
        final_video = await loop.run_in_executor(None, download_ytdl_video, url, out_tmpl)

        if not final_video or not os.path.exists(final_video):
            matches = glob.glob(f"tw_{m.chat.id}_{m.id}*")
            if matches:
                final_video = matches[0]

        if final_video and os.path.exists(final_video):
            bot_name = bot.me.username if bot.me else "MeowRoBot"
            await m.reply_video(
                video=final_video,
                caption=f"🐦 **Twitter / X Video Downloaded**\n**By @{bot_name} ⚡**"
            )
            await loading.delete()
        else:
            await loading.edit_text(font("❌ Could not download video from this URL. Make sure it's public and valid."))

    except Exception as e:
        await loading.edit_text(f"❌ **Error:** {e}")

    finally:
        for f in glob.glob(f"tw_{m.chat.id}_{m.id}*"):
            try:
                os.remove(f)
            except Exception:
                pass


@bot.on_message(filters.command(["tt", "tiktok"]) & ~filters.forwarded)
async def tiktok_handler(_, m: types.Message):
    if len(m.command) < 2:
        return await m.reply_text(font("❌ Please provide a TikTok URL.\nExample: `/tt https://vt.tiktok.com/...`"))

    url = m.command[1].strip()
    loading = await m.reply_text(font("⏳ Downloading TikTok video..."))
    out_tmpl = f"tt_{m.chat.id}_{m.id}.%(ext)s"
    final_video = None

    try:
        loop = asyncio.get_event_loop()
        final_video = await loop.run_in_executor(None, download_ytdl_video, url, out_tmpl)

        if not final_video or not os.path.exists(final_video):
            matches = glob.glob(f"tt_{m.chat.id}_{m.id}*")
            if matches:
                final_video = matches[0]

        if final_video and os.path.exists(final_video):
            bot_name = bot.me.username if bot.me else "MeowRoBot"
            await m.reply_video(
                video=final_video,
                caption=f"🎵 **TikTok Video Downloaded**\n**By @{bot_name} ⚡**"
            )
            await loading.delete()
        else:
            await loading.edit_text(font("❌ Could not download video from this TikTok link."))

    except Exception as e:
        await loading.edit_text(f"❌ **Error:** {e}")

    finally:
        for f in glob.glob(f"tt_{m.chat.id}_{m.id}*"):
            try:
                os.remove(f)
            except Exception:
                pass


@bot.on_message(filters.command(["pin", "pinterest"]) & ~filters.forwarded)
async def pin_handler(_, m: types.Message):
    if len(m.command) < 2:
        return await m.reply_text(font("❌ Please provide a query to search Pinterest.\nExample: `/pin cat wallpaper`"))

    query = m.text.split(maxsplit=1)[1]
    loading = await m.reply_text(font("⏳ Searching Pinterest..."))

    try:
        search_url = f"https://source.unsplash.com/1080x1920/?{query.replace(' ', '+')}"
        bot_name = bot.me.username if bot.me else "MeowRoBot"
        await m.reply_photo(search_url, caption=f"🎨 **Pinterest Search:** `{query}`\n**By @{bot_name} ⚡**")
        await loading.delete()
    except Exception as e:
        await loading.edit_text(f"❌ **Error:** {e}")
