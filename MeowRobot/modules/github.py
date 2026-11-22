#
# Copyright (C) 2021-2022 by TheAloneteam@Github, < https://github.com/TheAloneTeam >.
#
# All rights reserved.

import httpx
from pyrogram import filters, types

from MeowRobot import pbot as bot
from MeowRobot.utils.fonts import font

__mod_name__ = "GitHub"
__module__ = "𝐆ɪᴛʜᴜʙ🐙"

__help__ = """
*GitHub Explorer Module🐙*

*Commands:*  
❂ `/git [username]` — View complete profile and stats of a GitHub user  
❂ `/github [username]` — Same as `/git`  
❂ `/repo [owner/repo]` — View details, stars, and forks of a GitHub repository  
"""

@bot.on_message(filters.command(["git", "github"]) & ~filters.forwarded)
async def github_user(_, m: types.Message):
    if len(m.command) < 2:
        return await m.reply_text(font("❌ Usage: `/git [username]`"))

    username = m.command[1].strip().lstrip("@")
    status_msg = await m.reply_text(font("🔍 Fetching GitHub user data..."))

    url = f"https://api.github.com/users/{username}"
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url)
            if resp.status_code == 200:
                data = resp.json()
                name = data.get("name") or username
                bio = data.get("bio") or "No bio available."
                public_repos = data.get("public_repos", 0)
                followers = data.get("followers", 0)
                following = data.get("following", 0)
                company = data.get("company") or "None"
                location = data.get("location") or "Unknown"
                blog = data.get("blog") or "None"
                created_at = (data.get("created_at") or "").split("T")[0]
                avatar_url = data.get("avatar_url")
                profile_url = data.get("html_url")

                caption = (
                    f"🐙 **GitHub User:** [{name}]({profile_url})\n\n"
                    f"💬 **Bio:** `{bio}`\n"
                    f"📦 **Public Repos:** `{public_repos}`\n"
                    f"👥 **Followers:** `{followers}` | **Following:** `{following}`\n"
                    f"🏢 **Company:** `{company}`\n"
                    f"📍 **Location:** `{location}`\n"
                    f"🌐 **Website:** {blog}\n"
                    f"📅 **Joined:** `{created_at}`"
                )

                if avatar_url:
                    await m.reply_photo(photo=avatar_url, caption=caption)
                    await status_msg.delete()
                else:
                    await status_msg.edit_text(caption)
                return

        await status_msg.edit_text(font("❌ GitHub user not found!"))
    except Exception as e:
        await status_msg.edit_text(font(f"❌ Error: {e}"))


@bot.on_message(filters.command(["repo", "repository"]) & ~filters.forwarded)
async def github_repo(_, m: types.Message):
    if len(m.command) < 2 or "/" not in m.command[1]:
        return await m.reply_text(font("❌ Usage: `/repo [owner/repository]` (e.g. `/repo TheAloneTeam/MeowRoBot`)"))

    repo_path = m.command[1].strip()
    status_msg = await m.reply_text(font("🔍 Fetching repository details..."))

    url = f"https://api.github.com/repos/{repo_path}"
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url)
            if resp.status_code == 200:
                data = resp.json()
                repo_name = data.get("full_name")
                desc = data.get("description") or "No description provided."
                stars = data.get("stargazers_count", 0)
                forks = data.get("forks_count", 0)
                watchers = data.get("watchers_count", 0)
                issues = data.get("open_issues_count", 0)
                lang = data.get("language") or "Unknown"
                license_name = data.get("license", {}).get("name") if data.get("license") else "None"
                html_url = data.get("html_url")
                clone_url = data.get("clone_url")

                caption = (
                    f"📂 **Repository:** [{repo_name}]({html_url})\n\n"
                    f"📝 **Description:** `{desc}`\n"
                    f"⭐ **Stars:** `{stars}` | 🍴 **Forks:** `{forks}`\n"
                    f"👀 **Watchers:** `{watchers}` | 🐞 **Issues:** `{issues}`\n"
                    f"💻 **Language:** `{lang}`\n"
                    f"📜 **License:** `{license_name}`\n"
                    f"🔗 **Clone URL:** `{clone_url}`"
                )

                await status_msg.edit_text(caption)
                return

        await status_msg.edit_text(font("❌ Repository not found or is private!"))
    except Exception as e:
        await status_msg.edit_text(font(f"❌ Error: {e}"))
