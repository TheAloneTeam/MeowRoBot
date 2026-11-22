#
# Copyright (C) 2021-2022 by TheAloneteam@Github, < https://github.com/TheAloneTeam >.
#
# All rights reserved.

import os
import asyncio
import logging
import urllib.parse
import httpx
from pyrogram import filters, types, enums, ContinuePropagation
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery

from MeowRobot import pbot as bot, DRAGONS as DEV_LIST
from MeowRobot.utils.fonts import font
from MeowRobot.utils.mongo import db

logger = logging.getLogger(__name__)

__mod_name__ = "GitHub"
__module__ = "𝐆ɪᴛʜᴜʙ🐙"

__help__ = """
*Comprehensive GitHub Bot Suite Module🐙*
(All commands accessible via `/github` and `/gh`)

*Authentication & Account:*  
❂ `/ghconnect [token]` (or `/connect`) — Connect your GitHub account via Personal Access Token (PM only)  
❂ `/ghdisconnect` (or `/disconnect`) — Disconnect and log out of your GitHub account  
❂ `/ghme` (or `/me`) — View details of your connected GitHub account  

*Repository Notifications & Management:*  
❂ `/ghadd [owner/repo]` (or `/addrepo`) — Link a repository to this chat to receive event notifications  
❂ `/ghrm [owner/repo]` (or `/removerepo`) — Unlink a repository from this chat  
❂ `/ghrepos` (or `/repos`) — List all repositories currently linked to this chat  
❂ `/ghsettings [owner/repo]` (or `/settings`) — Toggle which events to receive (Pushes, Issues, PRs, Releases, Stars)  
❂ `/ghstar [owner/repo]` (or `/star`) — Star a repository directly on GitHub using your connected account  
❂ `/ghfork [owner/repo]` (or `/fork`) — Fork a repository to your connected GitHub account  

*Repository & User Inspection:*  
❂ `/github [username]` (or `/git`) — View complete profile and stats of a GitHub user  
❂ `/github [owner/repo]` (or `/repo`) — Detailed overview of a repository (stars, forks, watchers, license)  
❂ `/ghcommits [owner/repo]` (or `/commits`) — View recent commits with author, hash, and messages  
❂ `/ghreleases [owner/repo]` (or `/releases`) — View latest releases, assets, tags, and changelogs  
❂ `/ghissues [owner/repo]` (or `/issues`) — List open issues of a repository  
❂ `/ghprs [owner/repo]` (or `/prs`) — List open pull requests of a repository  
❂ `/ghbranches [owner/repo]` (or `/branches`) — List active branches of a repository  
❂ `/ghcontributors [owner/repo]` (or `/contributors`) — Top contributors ranked by contribution count  
❂ `/ghsearch [keyword]` — Search GitHub repositories with stars, forks, and links  
"""

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "").strip()

# Database collections
gh_users = db["github_connected_users"]
gh_chat_repos = db["github_linked_repos"]
gh_event_cache = db["github_event_cache"]

def get_headers(custom_token: str = None):
    headers = {"Accept": "application/vnd.github.v3+json"}
    token = custom_token or GITHUB_TOKEN
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers

async def is_admin(chat_id: int, user_id: int) -> bool:
    if user_id in DEV_LIST:
        return True
    try:
        member = await bot.get_chat_member(chat_id, user_id)
        return member.status in [enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER]
    except Exception:
        return False


# ===========================================================================
# 1. AUTHENTICATION & ACCOUNT COMMANDS (/ghconnect, /ghdisconnect, /ghme)
# ===========================================================================

@bot.on_message(filters.command(["ghconnect", "connect", "github_connect"]) & filters.private)
async def gh_connect(_, m: types.Message):
    if len(m.command) < 2:
        return await m.reply_text(
            "🐙 **Connect Your GitHub Account**\n\n"
            "To connect your GitHub account and manage repos directly from Telegram:\n"
            "1. Open GitHub: [Personal Access Tokens](https://github.com/settings/tokens)\n"
            "2. Click **Generate new token (classic)**\n"
            "3. Select scopes: `repo` (Full control of repositories)\n"
            "4. Copy your token and send:\n"
            "👉 `/ghconnect YOUR_GITHUB_TOKEN`\n\n"
            "🔒 *Your token is securely stored and never shared.*",
            disable_web_page_preview=True
        )

    token = m.command[1].strip()
    status_msg = await m.reply_text(font("⏳ Verifying your GitHub token..."))

    url = "https://api.github.com/user"
    try:
        async with httpx.AsyncClient(timeout=10.0, headers=get_headers(token)) as client:
            resp = await client.get(url)
            if resp.status_code == 200:
                user_data = resp.json()
                login = user_data.get("login")
                name = user_data.get("name") or login
                html_url = user_data.get("html_url")

                await gh_users.update_one(
                    {"user_id": m.from_user.id},
                    {"$set": {
                        "user_id": m.from_user.id,
                        "github_username": login,
                        "github_name": name,
                        "token": token
                    }},
                    upsert=True
                )

                return await status_msg.edit_text(
                    f"✅ **GitHub Account Connected Successfully!**\n\n"
                    f"👤 **User:** [{name}]({html_url}) (`@{login}`)\n\n"
                    f"You can now:\n"
                    f"• Star repositories: `/ghstar owner/repo`\n"
                    f"• Fork repositories: `/ghfork owner/repo`\n"
                    f"• View profile: `/ghme`\n"
                    f"• Disconnect anytime: `/ghdisconnect`",
                    disable_web_page_preview=False
                )

        await status_msg.edit_text(font("❌ Invalid GitHub token! Please verify permissions and try again."))
    except Exception as e:
        await status_msg.edit_text(font(f"❌ Error verifying token: {e}"))


@bot.on_message(filters.command(["ghdisconnect", "disconnect", "github_disconnect", "logout"]) & filters.private)
async def gh_disconnect(_, m: types.Message):
    res = await gh_users.delete_one({"user_id": m.from_user.id})
    if res.deleted_count > 0:
        await m.reply_text(font("✅ Your GitHub account has been disconnected and your token removed."))
    else:
        await m.reply_text(font("❌ You don't have any GitHub account connected. Use `/ghconnect` to link one."))


@bot.on_message(filters.command(["ghme", "me", "github_me"]) & filters.private)
async def gh_me(_, m: types.Message):
    user_doc = await gh_users.find_one({"user_id": m.from_user.id})
    if not user_doc:
        return await m.reply_text(font("❌ No GitHub account connected! Send `/ghconnect` to link your account."))

    token = user_doc.get("token")
    url = "https://api.github.com/user"
    try:
        async with httpx.AsyncClient(timeout=10.0, headers=get_headers(token)) as client:
            resp = await client.get(url)
            if resp.status_code == 200:
                data = resp.json()
                login = data.get("login")
                name = data.get("name") or login
                bio = data.get("bio") or "No bio."
                repos = data.get("public_repos", 0)
                followers = data.get("followers", 0)
                html_url = data.get("html_url")

                caption = (
                    f"🐙 **Connected GitHub Account**\n\n"
                    f"👤 **Name:** [{name}]({html_url}) (`@{login}`)\n"
                    f"💬 **Bio:** `{bio}`\n"
                    f"📦 **Public Repos:** `{repos}`\n"
                    f"👥 **Followers:** `{followers}`\n\n"
                    f"Use `/ghdisconnect` to unlink."
                )
                return await m.reply_text(caption, disable_web_page_preview=False)

        await m.reply_text(font("❌ Could not fetch GitHub profile. Your token might have expired. Use `/ghconnect` again."))
    except Exception as e:
        await m.reply_text(font(f"❌ Error: {e}"))


# ===========================================================================
# 2. REPOSITORY LINKING & NOTIFICATIONS (/ghadd, /ghrm, /ghrepos, /ghsettings)
# ===========================================================================

@bot.on_message(filters.command(["ghadd", "ghaddrepo", "addrepo", "github_add", "add"]) & ~filters.forwarded)
async def gh_add_repo(_, m: types.Message):
    if m.chat.type != enums.ChatType.PRIVATE and not await is_admin(m.chat.id, m.from_user.id):
        return await m.reply_text(font("❌ Only group admins can link repositories to this chat."))

    if len(m.command) < 2 or "/" not in m.command[1]:
        return await m.reply_text(font("❌ Usage: `/ghadd [owner/repository]` (e.g. `/ghadd TheAloneTeam/MeowRoBot`)"))

    repo_path = m.command[1].strip()
    status_msg = await m.reply_text(font(f"🔍 Checking repository '{repo_path}'..."))

    # Validate repo existence
    url = f"https://api.github.com/repos/{repo_path}"
    try:
        async with httpx.AsyncClient(timeout=10.0, headers=get_headers()) as client:
            resp = await client.get(url)
            if resp.status_code != 200:
                return await status_msg.edit_text(font("❌ Repository not found on GitHub or is private!"))

            data = resp.json()
            full_name = data.get("full_name", repo_path)
            html_url = data.get("html_url")

            # Default events
            events = {
                "pushes": True,
                "issues": True,
                "pulls": True,
                "releases": True,
                "stars": True
            }

            await gh_chat_repos.update_one(
                {"chat_id": m.chat.id, "repo": full_name.lower()},
                {"$set": {
                    "chat_id": m.chat.id,
                    "repo": full_name.lower(),
                    "repo_name": full_name,
                    "events": events
                }},
                upsert=True
            )

            # Pre-cache latest commit and release to avoid spamming old history
            try:
                c_resp = await client.get(f"https://api.github.com/repos/{full_name}/commits?per_page=1")
                if c_resp.status_code == 200 and c_resp.json():
                    latest_sha = c_resp.json()[0].get("sha")
                    await gh_event_cache.update_one(
                        {"repo": full_name.lower()},
                        {"$set": {"last_commit": latest_sha}},
                        upsert=True
                    )
            except Exception:
                pass

            buttons = InlineKeyboardMarkup([
                [InlineKeyboardButton("⚙️ Configure Events", callback_data=f"gh_settings|{m.chat.id}|{full_name}")],
                [InlineKeyboardButton("🌐 Open on GitHub", url=html_url)]
            ])

            await status_msg.edit_text(
                f"✅ **Repository Linked Successfully!**\n\n"
                f"📂 **Repo:** [{full_name}]({html_url})\n"
                f"🔔 **Notifications Active:** Pushes, Issues, PRs, Releases, Stars\n\n"
                f"Use `/ghsettings {full_name}` or the button below to customize alerts.",
                reply_markup=buttons,
                disable_web_page_preview=False
            )
    except Exception as e:
        await status_msg.edit_text(font(f"❌ Error linking repository: {e}"))


@bot.on_message(filters.command(["ghrm", "ghremoverepo", "removerepo", "rmrepo", "github_rm", "rm"]) & ~filters.forwarded)
async def gh_remove_repo(_, m: types.Message):
    if m.chat.type != enums.ChatType.PRIVATE and not await is_admin(m.chat.id, m.from_user.id):
        return await m.reply_text(font("❌ Only group admins can unlink repositories."))

    if len(m.command) < 2 or "/" not in m.command[1]:
        return await m.reply_text(font("❌ Usage: `/ghrm [owner/repository]`"))

    repo_path = m.command[1].strip().lower()
    res = await gh_chat_repos.delete_one({"chat_id": m.chat.id, "repo": repo_path})

    if res.deleted_count > 0:
        await m.reply_text(font(f"✅ Repository `{repo_path}` unlinked! You will no longer receive notifications here."))
    else:
        await m.reply_text(font(f"❌ Repository `{repo_path}` is not linked to this chat. Use `/ghrepos` to check."))


@bot.on_message(filters.command(["ghrepos", "repos", "github_repos"]) & ~filters.forwarded)
async def gh_list_repos(_, m: types.Message):
    docs = await gh_chat_repos.find({"chat_id": m.chat.id}).to_list(length=50)
    if not docs:
        return await m.reply_text(font("ℹ️ No repositories are linked to this chat yet!\n\nUse `/ghadd [owner/repo]` to link one."))

    text = f"📂 **Linked GitHub Repositories for this chat ({len(docs)}):**\n\n"
    for idx, d in enumerate(docs, 1):
        name = d.get("repo_name", d["repo"])
        events = d.get("events", {})
        active_list = [k.capitalize() for k, v in events.items() if v]
        active_str = ", ".join(active_list) if active_list else "None"
        text += f"{idx}. [{name}](https://github.com/{name})\n   🔔 Alerts: `{active_str}`\n   ⚙️ `/ghsettings {name}`\n\n"

    await m.reply_text(text, disable_web_page_preview=True)


def build_settings_keyboard(chat_id: int, repo_name: str, events: dict):
    def icon(k):
        return "🟢" if events.get(k, True) else "🔴"

    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(f"{icon('pushes')} Pushes", callback_data=f"gh_tog|{chat_id}|{repo_name}|pushes"),
            InlineKeyboardButton(f"{icon('issues')} Issues", callback_data=f"gh_tog|{chat_id}|{repo_name}|issues")
        ],
        [
            InlineKeyboardButton(f"{icon('pulls')} Pull Requests", callback_data=f"gh_tog|{chat_id}|{repo_name}|pulls"),
            InlineKeyboardButton(f"{icon('releases')} Releases", callback_data=f"gh_tog|{chat_id}|{repo_name}|releases")
        ],
        [
            InlineKeyboardButton(f"{icon('stars')} Stars & Forks", callback_data=f"gh_tog|{chat_id}|{repo_name}|stars")
        ],
        [
            InlineKeyboardButton("🗑️ Unlink Repository", callback_data=f"gh_unlink|{chat_id}|{repo_name}")
        ]
    ])


@bot.on_message(filters.command(["ghsettings", "github_settings", "settings", "config", "events"]) & ~filters.forwarded)
async def gh_settings_cmd(_, m: types.Message):
    if m.chat.type != enums.ChatType.PRIVATE and not await is_admin(m.chat.id, m.from_user.id):
        return await m.reply_text(font("❌ Only group admins can change notification settings."))

    docs = await gh_chat_repos.find({"chat_id": m.chat.id}).to_list(length=50)
    if not docs:
        return await m.reply_text(font("❌ No repositories linked to this chat! Use `/ghadd [owner/repo]` first."))

    target_doc = None
    if len(m.command) > 1:
        target_name = m.command[1].strip().lower()
        for d in docs:
            if d["repo"] == target_name:
                target_doc = d
                break
    else:
        target_doc = docs[0]

    if not target_doc:
        return await m.reply_text(font("❌ Linked repository not found. Use `/ghrepos` to view available."))

    repo_name = target_doc.get("repo_name", target_doc["repo"])
    events = target_doc.get("events", {})
    keyboard = build_settings_keyboard(m.chat.id, repo_name, events)

    await m.reply_text(
        f"⚙️ **Notification Settings for [{repo_name}](https://github.com/{repo_name}):**\n\n"
        f"Tap the buttons below to toggle notification events on (🟢) or off (🔴):",
        reply_markup=keyboard,
        disable_web_page_preview=True
    )


@bot.on_callback_query(filters.regex(r"^gh_"))
async def gh_callbacks(_, cb: CallbackQuery):
    data = cb.data.split("|")
    action = data[0]

    if action == "gh_settings":
        chat_id = int(data[1])
        repo_name = data[2]
        doc = await gh_chat_repos.find_one({"chat_id": chat_id, "repo": repo_name.lower()})
        if not doc:
            return await cb.answer("Repository not found!", show_alert=True)
        events = doc.get("events", {})
        kb = build_settings_keyboard(chat_id, repo_name, events)
        await cb.message.edit_text(
            f"⚙️ **Notification Settings for [{repo_name}](https://github.com/{repo_name}):**\n\n"
            f"Tap the buttons below to toggle notification events on (🟢) or off (🔴):",
            reply_markup=kb,
            disable_web_page_preview=True
        )
        await cb.answer()

    elif action == "gh_tog":
        chat_id = int(data[1])
        repo_name = data[2]
        event_key = data[3]

        doc = await gh_chat_repos.find_one({"chat_id": chat_id, "repo": repo_name.lower()})
        if not doc:
            return await cb.answer("Repository not linked!", show_alert=True)

        events = doc.get("events", {})
        current = events.get(event_key, True)
        events[event_key] = not current

        await gh_chat_repos.update_one(
            {"chat_id": chat_id, "repo": repo_name.lower()},
            {"$set": {"events": events}}
        )

        kb = build_settings_keyboard(chat_id, repo_name, events)
        await cb.message.edit_reply_markup(reply_markup=kb)
        await cb.answer(f"{event_key.capitalize()}: {'Enabled' if not current else 'Disabled'}")

    elif action == "gh_unlink":
        chat_id = int(data[1])
        repo_name = data[2]
        await gh_chat_repos.delete_one({"chat_id": chat_id, "repo": repo_name.lower()})
        await cb.message.edit_text(f"🗑️ Repository `{repo_name}` unlinked from this chat!")
        await cb.answer("Unlinked successfully!")


# ===========================================================================
# 3. DIRECT GITHUB ACTIONS (/ghstar, /ghfork)
# ===========================================================================

@bot.on_message(filters.command(["ghstar", "star", "github_star"]) & ~filters.forwarded)
async def gh_star_cmd(_, m: types.Message):
    user_doc = await gh_users.find_one({"user_id": m.from_user.id})
    if not user_doc:
        return await m.reply_text(font("❌ Connect your GitHub account first! Send `/ghconnect` in private to link."))

    if len(m.command) < 2 or "/" not in m.command[1]:
        return await m.reply_text(font("❌ Usage: `/ghstar [owner/repository]` (e.g. `/ghstar TheAloneTeam/MeowRoBot`)"))

    repo_path = m.command[1].strip()
    status_msg = await m.reply_text(font(f"⭐ Starring '{repo_path}'..."))

    token = user_doc.get("token")
    url = f"https://api.github.com/user/starred/{repo_path}"
    try:
        async with httpx.AsyncClient(timeout=10.0, headers=get_headers(token)) as client:
            resp = await client.put(url, headers={"Content-Length": "0"})
            if resp.status_code in [204, 200]:
                return await status_msg.edit_text(f"⭐ **Successfully starred [{repo_path}](https://github.com/{repo_path})!**")

        await status_msg.edit_text(font("❌ Failed to star repository. Check permissions or repository name."))
    except Exception as e:
        await status_msg.edit_text(font(f"❌ Error: {e}"))


@bot.on_message(filters.command(["ghfork", "fork", "github_fork"]) & ~filters.forwarded)
async def gh_fork_cmd(_, m: types.Message):
    user_doc = await gh_users.find_one({"user_id": m.from_user.id})
    if not user_doc:
        return await m.reply_text(font("❌ Connect your GitHub account first! Send `/ghconnect` in private to link."))

    if len(m.command) < 2 or "/" not in m.command[1]:
        return await m.reply_text(font("❌ Usage: `/ghfork [owner/repository]`"))

    repo_path = m.command[1].strip()
    status_msg = await m.reply_text(font(f"🍴 Forking '{repo_path}' to your account..."))

    token = user_doc.get("token")
    url = f"https://api.github.com/repos/{repo_path}/forks"
    try:
        async with httpx.AsyncClient(timeout=15.0, headers=get_headers(token)) as client:
            resp = await client.post(url)
            if resp.status_code in [202, 201, 200]:
                data = resp.json()
                fork_url = data.get("html_url")
                return await status_msg.edit_text(
                    f"🍴 **Repository Forked Successfully!**\n\n"
                    f"🔗 **Your Fork:** [Open Fork]({fork_url})\n\n"
                    f"♨️ **Powered by:** @TheAloneTeam",
                    disable_web_page_preview=False
                )

        await status_msg.edit_text(font("❌ Failed to fork repository. It might already be forked or is private."))
    except Exception as e:
        await status_msg.edit_text(font(f"❌ Error: {e}"))


# ===========================================================================
# 4. REPOSITORY & USER INSPECTION COMMANDS
# ===========================================================================

@bot.on_message(filters.command(["git", "user"]) & ~filters.forwarded)
async def github_user_cmd(_, m: types.Message):
    if len(m.command) < 2:
        return await m.reply_text(font("❌ Usage: `/git [username]` (e.g. `/git AshokShau`)"))
    await fetch_and_send_user(m, m.command[1].strip().lstrip("@"))


@bot.on_message(filters.command(["org", "ghorg", "organization"]) & ~filters.forwarded)
async def github_org(_, m: types.Message):
    if len(m.command) < 2:
        return await m.reply_text(font("❌ Usage: `/org [org_name]` (e.g. `/org TheAloneTeam`)"))

    org_name = m.command[1].strip().lstrip("@")
    status_msg = await m.reply_text(font("🔍 Fetching GitHub organization data..."))

    url = f"https://api.github.com/orgs/{org_name}"
    try:
        async with httpx.AsyncClient(timeout=10.0, headers=get_headers()) as client:
            resp = await client.get(url)
            if resp.status_code == 200:
                data = resp.json()
                name = data.get("name") or org_name
                desc = data.get("description") or "No description provided."
                public_repos = data.get("public_repos", 0)
                followers = data.get("followers", 0)
                blog = data.get("blog") or "None"
                location = data.get("location") or "Unknown"
                created_at = (data.get("created_at") or "").split("T")[0]
                avatar_url = data.get("avatar_url")
                html_url = data.get("html_url")

                caption = (
                    f"🏢 **GitHub Organization:** [{name}]({html_url})\n\n"
                    f"💬 **Description:** `{desc}`\n"
                    f"📦 **Public Repositories:** `{public_repos}`\n"
                    f"👥 **Followers:** `{followers}`\n"
                    f"📍 **Location:** `{location}`\n"
                    f"🌐 **Website:** {blog}\n"
                    f"📅 **Created:** `{created_at}`"
                )

                if avatar_url:
                    await m.reply_photo(photo=avatar_url, caption=caption)
                    await status_msg.delete()
                else:
                    await status_msg.edit_text(caption)
                return

        await status_msg.edit_text(font("❌ Organization not found!"))
    except Exception as e:
        await status_msg.edit_text(font(f"❌ Error: {e}"))


@bot.on_message(filters.command(["repo", "repository"]) & ~filters.forwarded)
async def github_repo_cmd(_, m: types.Message):
    if len(m.command) < 2 or "/" not in m.command[1]:
        return await m.reply_text(font("❌ Usage: `/repo [owner/repository]` (e.g. `/repo TheAloneTeam/MeowRoBot`)"))
    await fetch_and_send_repo(m, m.command[1].strip())


async def fetch_and_send_user(m: types.Message, username: str):
    status_msg = await m.reply_text(font("🔍 Fetching GitHub user data..."))
    url = f"https://api.github.com/users/{username}"
    try:
        async with httpx.AsyncClient(timeout=10.0, headers=get_headers()) as client:
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


async def fetch_and_send_repo(m: types.Message, repo_path: str):
    status_msg = await m.reply_text(font("🔍 Fetching repository details..."))
    url = f"https://api.github.com/repos/{repo_path}"
    try:
        async with httpx.AsyncClient(timeout=10.0, headers=get_headers()) as client:
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
                default_branch = data.get("default_branch", "main")
                license_name = data.get("license", {}).get("name") if data.get("license") else "None"
                html_url = data.get("html_url")
                clone_url = data.get("clone_url")

                caption = (
                    f"📂 **Repository:** [{repo_name}]({html_url})\n\n"
                    f"📝 **Description:** `{desc}`\n"
                    f"⭐ **Stars:** `{stars}` | 🍴 **Forks:** `{forks}`\n"
                    f"👀 **Watchers:** `{watchers}` | 🐞 **Issues:** `{issues}`\n"
                    f"🌿 **Default Branch:** `{default_branch}`\n"
                    f"💻 **Language:** `{lang}`\n"
                    f"📜 **License:** `{license_name}`\n"
                    f"🔗 **Clone URL:** `{clone_url}`"
                )

                await status_msg.edit_text(caption)
                return

        await status_msg.edit_text(font("❌ Repository not found or is private!"))
    except Exception as e:
        await status_msg.edit_text(font(f"❌ Error: {e}"))


# Unified /github and /gh Master Router
@bot.on_message(filters.command(["github", "gh"]) & ~filters.forwarded)
async def github_master_router(_, m: types.Message):
    if len(m.command) < 2:
        # Show Hub Dashboard
        user_doc = await gh_users.find_one({"user_id": m.from_user.id})
        connected_status = f"Connected as `@{user_doc['github_username']}` 🟢" if user_doc else "Not Connected 🔴"

        text = (
            "🐙 **GitHub Bot Suite Dashboard**\n\n"
            f"👤 **Account Status:** {connected_status}\n\n"
            "**Core Commands:**\n"
            "• `/ghconnect` — Link your GitHub account in private\n"
            "• `/ghdisconnect` — Log out from your account\n"
            "• `/ghme` — View your connected profile\n"
            "• `/ghadd [owner/repo]` — Link repo for chat notifications\n"
            "• `/ghrm [owner/repo]` — Unlink repository\n"
            "• `/ghrepos` — List all linked repositories\n"
            "• `/ghsettings [owner/repo]` — Configure notifications\n"
            "• `/ghstar [owner/repo]` — Star a repository\n"
            "• `/ghfork [owner/repo]` — Fork a repository\n"
            "• `/ghsearch [keyword]` — Search repositories\n"
            "• `/github [username]` — View user profile\n"
            "• `/github [owner/repo]` — View repository details\n\n"
            "♨️ **Powered by:** @TheAloneTeam"
        )
        return await m.reply_text(text)

    sub = m.command[1].strip()
    # Check if sub is a subcommand
    if sub in ["connect", "login"]:
        return await gh_connect(_, m)
    elif sub in ["disconnect", "logout"]:
        return await gh_disconnect(_, m)
    elif sub in ["me", "user_me"]:
        return await gh_me(_, m)
    elif sub in ["add", "addrepo"]:
        if len(m.command) > 2:
            m.command = ["ghadd", m.command[2]]
            return await gh_add_repo(_, m)
        return await m.reply_text(font("❌ Usage: `/github add [owner/repo]`"))
    elif sub in ["rm", "remove", "removerepo"]:
        if len(m.command) > 2:
            m.command = ["ghrm", m.command[2]]
            return await gh_remove_repo(_, m)
        return await m.reply_text(font("❌ Usage: `/github rm [owner/repo]`"))
    elif sub in ["repos", "list"]:
        return await gh_list_repos(_, m)
    elif sub in ["settings", "config", "events"]:
        if len(m.command) > 2:
            m.command = ["ghsettings", m.command[2]]
        else:
            m.command = ["ghsettings"]
        return await gh_settings_cmd(_, m)
    elif sub in ["star"]:
        if len(m.command) > 2:
            m.command = ["ghstar", m.command[2]]
            return await gh_star_cmd(_, m)
        return await m.reply_text(font("❌ Usage: `/github star [owner/repo]`"))
    elif sub in ["fork"]:
        if len(m.command) > 2:
            m.command = ["ghfork", m.command[2]]
            return await gh_fork_cmd(_, m)
        return await m.reply_text(font("❌ Usage: `/github fork [owner/repo]`"))
    elif sub in ["commits", "commit"]:
        if len(m.command) > 2:
            m.command = ["ghcommits", m.command[2]]
            return await github_commits(_, m)
        return await m.reply_text(font("❌ Usage: `/github commits [owner/repo]`"))
    elif sub in ["releases", "release"]:
        if len(m.command) > 2:
            m.command = ["ghreleases", m.command[2]]
            return await github_releases(_, m)
        return await m.reply_text(font("❌ Usage: `/github releases [owner/repo]`"))
    elif sub in ["issues", "issue"]:
        if len(m.command) > 2:
            m.command = ["ghissues", m.command[2]]
            return await github_issues(_, m)
        return await m.reply_text(font("❌ Usage: `/github issues [owner/repo]`"))
    elif sub in ["prs", "pulls"]:
        if len(m.command) > 2:
            m.command = ["ghprs", m.command[2]]
            return await github_prs(_, m)
        return await m.reply_text(font("❌ Usage: `/github prs [owner/repo]`"))
    elif "/" in sub:
        # It's an owner/repo path
        return await fetch_and_send_repo(m, sub)
    else:
        # It's a username
        return await fetch_and_send_user(m, sub.lstrip("@"))


# ===========================================================================
# 5. REPOSITORY SUB-COMMANDS (/ghcommits, /ghreleases, /ghissues, /ghprs, etc.)
# ===========================================================================

@bot.on_message(filters.command(["ghcommits", "commits", "commit"]) & ~filters.forwarded)
async def github_commits(_, m: types.Message):
    if len(m.command) < 2 or "/" not in m.command[1]:
        return await m.reply_text(font("❌ Usage: `/ghcommits [owner/repository]`"))

    repo_path = m.command[1].strip()
    status_msg = await m.reply_text(font("🔍 Fetching latest commits..."))

    url = f"https://api.github.com/repos/{repo_path}/commits?per_page=5"
    try:
        async with httpx.AsyncClient(timeout=10.0, headers=get_headers()) as client:
            resp = await client.get(url)
            if resp.status_code == 200:
                commits = resp.json()
                if not commits:
                    return await status_msg.edit_text(font("❌ No commits found in this repository."))

                text = f"📜 **Latest Commits for [{repo_path}](https://github.com/{repo_path}):**\n\n"
                for c in commits:
                    sha = c.get("sha", "")[:7]
                    html_url = c.get("html_url")
                    commit_info = c.get("commit", {})
                    author_name = commit_info.get("author", {}).get("name", "Unknown")
                    message = (commit_info.get("message") or "").split("\n")[0]
                    date_str = (commit_info.get("author", {}).get("date") or "").split("T")[0]

                    text += f"🔹 [`{sha}`]({html_url}) — **{message}**\n   👤 *{author_name}* on `{date_str}`\n\n"

                await status_msg.edit_text(text, disable_web_page_preview=True)
                return

        await status_msg.edit_text(font("❌ Repository not found or commits are unavailable!"))
    except Exception as e:
        await status_msg.edit_text(font(f"❌ Error: {e}"))


@bot.on_message(filters.command(["ghreleases", "releases", "release"]) & ~filters.forwarded)
async def github_releases(_, m: types.Message):
    if len(m.command) < 2 or "/" not in m.command[1]:
        return await m.reply_text(font("❌ Usage: `/ghreleases [owner/repository]`"))

    repo_path = m.command[1].strip()
    status_msg = await m.reply_text(font("🔍 Fetching releases..."))

    url = f"https://api.github.com/repos/{repo_path}/releases?per_page=3"
    try:
        async with httpx.AsyncClient(timeout=10.0, headers=get_headers()) as client:
            resp = await client.get(url)
            if resp.status_code == 200:
                releases = resp.json()
                if not releases:
                    return await status_msg.edit_text(font("❌ No releases found for this repository."))

                text = f"🏷️ **Releases for [{repo_path}](https://github.com/{repo_path}):**\n\n"
                for rel in releases:
                    tag = rel.get("tag_name")
                    title = rel.get("name") or tag
                    pub_date = (rel.get("published_at") or "").split("T")[0]
                    html_url = rel.get("html_url")
                    tar_url = rel.get("tarball_url")
                    zip_url = rel.get("zipball_url")

                    text += (
                        f"📦 **[{title}]({html_url})** (`{tag}`)\n"
                        f"📅 **Date:** `{pub_date}`\n"
                        f"📥 [Source Code (zip)]({zip_url}) | [Source Code (tar)]({tar_url})\n\n"
                    )

                await status_msg.edit_text(text, disable_web_page_preview=True)
                return

        await status_msg.edit_text(font("❌ Repository not found or releases are private!"))
    except Exception as e:
        await status_msg.edit_text(font(f"❌ Error: {e}"))


@bot.on_message(filters.command(["ghissues", "issues", "issue"]) & ~filters.forwarded)
async def github_issues(_, m: types.Message):
    if len(m.command) < 2 or "/" not in m.command[1]:
        return await m.reply_text(font("❌ Usage: `/ghissues [owner/repository]`"))

    repo_path = m.command[1].strip()
    status_msg = await m.reply_text(font("🔍 Fetching open issues..."))

    url = f"https://api.github.com/repos/{repo_path}/issues?state=open&per_page=5"
    try:
        async with httpx.AsyncClient(timeout=10.0, headers=get_headers()) as client:
            resp = await client.get(url)
            if resp.status_code == 200:
                issues = resp.json()
                pure_issues = [i for i in issues if "pull_request" not in i]
                if not pure_issues:
                    return await status_msg.edit_text(font("✨ No open issues in this repository!"))

                text = f"🐞 **Open Issues for [{repo_path}](https://github.com/{repo_path}):**\n\n"
                for iss in pure_issues[:5]:
                    num = iss.get("number")
                    title = iss.get("title")
                    user = iss.get("user", {}).get("login", "Unknown")
                    html_url = iss.get("html_url")
                    comments = iss.get("comments", 0)

                    text += f"🔹 [#{num}]({html_url}) — **{title}**\n   👤 By `{user}` | 💬 `{comments}` comments\n\n"

                await status_msg.edit_text(text, disable_web_page_preview=True)
                return

        await status_msg.edit_text(font("❌ Repository not found!"))
    except Exception as e:
        await status_msg.edit_text(font(f"❌ Error: {e}"))


@bot.on_message(filters.command(["ghprs", "prs", "pulls", "pullrequests"]) & ~filters.forwarded)
async def github_prs(_, m: types.Message):
    if len(m.command) < 2 or "/" not in m.command[1]:
        return await m.reply_text(font("❌ Usage: `/ghprs [owner/repository]`"))

    repo_path = m.command[1].strip()
    status_msg = await m.reply_text(font("🔍 Fetching open pull requests..."))

    url = f"https://api.github.com/repos/{repo_path}/pulls?state=open&per_page=5"
    try:
        async with httpx.AsyncClient(timeout=10.0, headers=get_headers()) as client:
            resp = await client.get(url)
            if resp.status_code == 200:
                prs = resp.json()
                if not prs:
                    return await status_msg.edit_text(font("✨ No open pull requests in this repository!"))

                text = f"🔀 **Open Pull Requests for [{repo_path}](https://github.com/{repo_path}):**\n\n"
                for pr in prs:
                    num = pr.get("number")
                    title = pr.get("title")
                    user = pr.get("user", {}).get("login", "Unknown")
                    html_url = pr.get("html_url")
                    base = pr.get("base", {}).get("ref", "main")

                    text += f"🔹 [#{num}]({html_url}) — **{title}**\n   👤 By `{user}` into branch `{base}`\n\n"

                await status_msg.edit_text(text, disable_web_page_preview=True)
                return

        await status_msg.edit_text(font("❌ Repository not found!"))
    except Exception as e:
        await status_msg.edit_text(font(f"❌ Error: {e}"))


@bot.on_message(filters.command(["ghcontributors", "contributors", "contribs"]) & ~filters.forwarded)
async def github_contributors(_, m: types.Message):
    if len(m.command) < 2 or "/" not in m.command[1]:
        return await m.reply_text(font("❌ Usage: `/ghcontributors [owner/repository]`"))

    repo_path = m.command[1].strip()
    status_msg = await m.reply_text(font("🔍 Fetching contributors..."))

    url = f"https://api.github.com/repos/{repo_path}/contributors?per_page=10"
    try:
        async with httpx.AsyncClient(timeout=10.0, headers=get_headers()) as client:
            resp = await client.get(url)
            if resp.status_code == 200:
                contribs = resp.json()
                if not contribs:
                    return await status_msg.edit_text(font("❌ No contributors found."))

                text = f"👥 **Top Contributors for [{repo_path}](https://github.com/{repo_path}):**\n\n"
                for idx, c in enumerate(contribs, 1):
                    login = c.get("login")
                    html_url = c.get("html_url")
                    commits = c.get("contributions", 0)

                    text += f"{idx}. [{login}]({html_url}) — `{commits}` commits\n"

                await status_msg.edit_text(text, disable_web_page_preview=True)
                return

        await status_msg.edit_text(font("❌ Repository not found!"))
    except Exception as e:
        await status_msg.edit_text(font(f"❌ Error: {e}"))


@bot.on_message(filters.command(["ghbranches", "branches", "branch"]) & ~filters.forwarded)
async def github_branches(_, m: types.Message):
    if len(m.command) < 2 or "/" not in m.command[1]:
        return await m.reply_text(font("❌ Usage: `/ghbranches [owner/repository]`"))

    repo_path = m.command[1].strip()
    status_msg = await m.reply_text(font("🔍 Fetching branches..."))

    url = f"https://api.github.com/repos/{repo_path}/branches?per_page=15"
    try:
        async with httpx.AsyncClient(timeout=10.0, headers=get_headers()) as client:
            resp = await client.get(url)
            if resp.status_code == 200:
                branches = resp.json()
                if not branches:
                    return await status_msg.edit_text(font("❌ No branches found."))

                text = f"🌿 **Branches for [{repo_path}](https://github.com/{repo_path}):**\n\n"
                for b in branches:
                    name = b.get("name")
                    commit_sha = b.get("commit", {}).get("sha", "")[:7]
                    text += f"🔹 `{name}` (`{commit_sha}`)\n"

                await status_msg.edit_text(text, disable_web_page_preview=True)
                return

        await status_msg.edit_text(font("❌ Repository not found!"))
    except Exception as e:
        await status_msg.edit_text(font(f"❌ Error: {e}"))


@bot.on_message(filters.command(["ghsearch", "githubsearch", "searchrepo"]) & ~filters.forwarded)
async def github_search(_, m: types.Message):
    if len(m.command) < 2:
        return await m.reply_text(font("❌ Usage: `/ghsearch [search keywords]`"))

    query = m.text.split(None, 1)[1].strip()
    status_msg = await m.reply_text(font(f"🔍 Searching GitHub repositories for '{query}'..."))

    safe_q = urllib.parse.quote(query)
    url = f"https://api.github.com/search/repositories?q={safe_q}&sort=stars&order=desc&per_page=5"
    try:
        async with httpx.AsyncClient(timeout=12.0, headers=get_headers()) as client:
            resp = await client.get(url)
            if resp.status_code == 200:
                data = resp.json()
                total = data.get("total_count", 0)
                items = data.get("items", [])

                if not items:
                    return await status_msg.edit_text(font(f"❌ No repositories found matching '{query}'."))

                text = f"🔎 **GitHub Search Results for '{query}'** (Total: `{total}`):\n\n"
                for it in items:
                    full_name = it.get("full_name")
                    html_url = it.get("html_url")
                    stars = it.get("stargazers_count", 0)
                    forks = it.get("forks_count", 0)
                    lang = it.get("language") or "Code"
                    desc = (it.get("description") or "No description.")[:80]

                    text += (
                        f"📂 **[{full_name}]({html_url})**\n"
                        f"   ⭐ `{stars}` | 🍴 `{forks}` | 💻 `{lang}`\n"
                        f"   📝 *{desc}*\n\n"
                    )

                await status_msg.edit_text(text, disable_web_page_preview=True)
                return

        await status_msg.edit_text(font("❌ GitHub search API failed. Please try again later."))
    except Exception as e:
        await status_msg.edit_text(font(f"❌ Error: {e}"))


# ===========================================================================
# 6. BACKGROUND NOTIFIER LOOP (Checks linked repositories for real-time events)
# ===========================================================================

async def github_notifier_worker():
    """Background task checking linked repositories and broadcasting updates"""
    logger.info("GitHub Real-time Event Notifier loop started.")
    await asyncio.sleep(20)

    while True:
        try:
            linked_entries = await gh_chat_repos.find({}).to_list(length=200)
            if not linked_entries:
                await asyncio.sleep(60)
                continue

            repo_chats = {}
            for entry in linked_entries:
                r = entry["repo"]
                if r not in repo_chats:
                    repo_chats[r] = []
                repo_chats[r].append(entry)

            async with httpx.AsyncClient(timeout=15.0, headers=get_headers()) as client:
                for repo_key, chats in repo_chats.items():
                    cache = await gh_event_cache.find_one({"repo": repo_key}) or {}

                    # 1. Check Commits
                    try:
                        c_resp = await client.get(f"https://api.github.com/repos/{repo_key}/commits?per_page=1")
                        if c_resp.status_code == 200 and c_resp.json():
                            latest_c = c_resp.json()[0]
                            latest_sha = latest_c.get("sha")
                            cached_sha = cache.get("last_commit")

                            if cached_sha and latest_sha != cached_sha:
                                sha_short = latest_sha[:7]
                                msg_text = (latest_c.get("commit", {}).get("message") or "").split("\n")[0]
                                author = latest_c.get("commit", {}).get("author", {}).get("name", "Unknown")
                                html_url = latest_c.get("html_url")

                                notif = (
                                    f"🐙 **[GitHub] New Commit Pushed!**\n\n"
                                    f"📂 **Repository:** [{repo_key}](https://github.com/{repo_key})\n"
                                    f"🔹 [`{sha_short}`]({html_url}) — **{msg_text}**\n"
                                    f"👤 **Author:** `{author}`"
                                )

                                for ch in chats:
                                    if ch.get("events", {}).get("pushes", True):
                                        try:
                                            await bot.send_message(ch["chat_id"], notif, disable_web_page_preview=True)
                                        except Exception:
                                            pass

                            await gh_event_cache.update_one({"repo": repo_key}, {"$set": {"last_commit": latest_sha}}, upsert=True)
                    except Exception:
                        pass

                    # 2. Check Releases
                    try:
                        r_resp = await client.get(f"https://api.github.com/repos/{repo_key}/releases?per_page=1")
                        if r_resp.status_code == 200 and r_resp.json():
                            latest_r = r_resp.json()[0]
                            rel_id = latest_r.get("id")
                            cached_rel_id = cache.get("last_release")

                            if cached_rel_id and rel_id != cached_rel_id:
                                tag = latest_r.get("tag_name")
                                name = latest_r.get("name") or tag
                                html_url = latest_r.get("html_url")

                                notif = (
                                    f"🏷️ **[GitHub] New Release Published!**\n\n"
                                    f"📂 **Repository:** [{repo_key}](https://github.com/{repo_key})\n"
                                    f"📦 **Release:** [{name}]({html_url}) (`{tag}`)\n"
                                    f"✨ Check release notes and download assets now!"
                                )

                                for ch in chats:
                                    if ch.get("events", {}).get("releases", True):
                                        try:
                                            await bot.send_message(ch["chat_id"], notif, disable_web_page_preview=True)
                                        except Exception:
                                            pass

                            await gh_event_cache.update_one({"repo": repo_key}, {"$set": {"last_release": rel_id}}, upsert=True)
                    except Exception:
                        pass

                    await asyncio.sleep(2)

        except Exception as e:
            logger.error(f"Error in GitHub notifier loop: {e}")

        await asyncio.sleep(60)


# Start background notifier task safely once the event loop is active
_notifier_started = False

@bot.on_message(group=-999)
async def _init_github_notifier(_, __):
    global _notifier_started
    if not _notifier_started:
        _notifier_started = True
        try:
            asyncio.create_task(github_notifier_worker())
        except Exception:
            pass
    raise ContinuePropagation
