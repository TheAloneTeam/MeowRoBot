#
# Copyright (C) 2021-2026 by TheAloneTeam@Github, < https://github.com/TheAloneTeam >.
# This file is part of < https://github.com/TheAloneTeam/MeowRobot > project,
# and is released under the "MIT License Agreement".
# Please see < https://github.com/TheAloneTeam/MeowRobot/blob/master/LICENSE >
#
# All rights reserved.

import os


class Config(object):
    LOGGER = True

    # Telegram API credentials from my.telegram.org/apps
    API_ID = int(os.environ.get("API_ID", 0)) if os.environ.get("API_ID") else None
    API_HASH = os.environ.get("API_HASH", None)

    # Telegram Bot Token from @BotFather
    TOKEN = os.environ.get("TOKEN", None)

    # Telegram User ID of the bot owner
    OWNER_ID = int(os.environ.get("OWNER_ID", 0)) if os.environ.get("OWNER_ID") else None

    # Databases
    DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///sqldb.db")
    MONGO_DB_URI = os.environ.get("MONGO_DB_URI", None)

    # Logging Channel
    EVENT_LOGS = os.environ.get("EVENT_LOGS", None)

    # AI Chatbot Integration
    CHATBOT_API_URL = os.environ.get("CHATBOT_API_URL", "https://chatbot.riteshyt.in/api/chat")
    CHATBOT_API_KEY = os.environ.get("CHATBOT_API_KEY", None)

    # Community & Support
    SUPPORT_CHAT = os.environ.get("SUPPORT_CHAT", "TeamAashik")
    SUPPORT_CHANNEL = os.environ.get("SUPPORT_CHANNEL", "AashikTeam")

    # Banner image for start message
    START_IMG = os.environ.get(
        "START_IMG", "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=800"
    )

    # External APIs
    CASH_API_KEY = os.environ.get("CASH_API_KEY", None)
    TIME_API_KEY = os.environ.get("TIME_API_KEY", None)

    # NSFW Filtering
    NSFW_LOG_CHANNEL = os.environ.get("NSFW_LOG_CHANNEL", None)
    NSFW_STORAGE = os.environ.get("NSFW_STORAGE", None)

    # Privileged User Lists
    BL_CHATS = set(int(x) for x in os.environ.get("BL_CHATS", "").split() if x.strip().isdigit())
    DRAGONS = set(int(x) for x in os.environ.get("DRAGONS", "").split() if x.strip().isdigit())
    DEV_USERS = set(int(x) for x in os.environ.get("DEV_USERS", "").split() if x.strip().isdigit())
    DEMONS = set(int(x) for x in os.environ.get("DEMONS", "").split() if x.strip().isdigit())
    TIGERS = set(int(x) for x in os.environ.get("TIGERS", "").split() if x.strip().isdigit())
    WOLVES = set(int(x) for x in os.environ.get("WOLVES", "").split() if x.strip().isdigit())

    # Operational Flags
    ALLOW_CHATS = bool(os.environ.get("ALLOW_CHATS", True))
    ALLOW_EXCL = bool(os.environ.get("ALLOW_EXCL", True))
    DEL_CMDS = bool(os.environ.get("DEL_CMDS", True))
    INFOPIC = bool(os.environ.get("INFOPIC", True))
    STRICT_GBAN = bool(os.environ.get("STRICT_GBAN", True))
    TEMP_DOWNLOAD_DIRECTORY = os.environ.get("TEMP_DOWNLOAD_DIRECTORY", "./")
    WORKERS = int(os.environ.get("WORKERS", 8))

    LOAD = os.environ.get("LOAD", "").split()
    NO_LOAD = os.environ.get("NO_LOAD", "").split()


class Production(Config):
    LOGGER = True


class Development(Config):
    LOGGER = True
