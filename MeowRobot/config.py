#
# Copyright (C) 2021-2022 by TheAloneteam@Github, < https://github.com/TheAloneTeam >.
# This file is part of < https://github.com/TheAloneTeam/MeowRobot > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/TheAloneTeam/MeowRobot/blob/master/LICENSE >
#
# All rights reserved.

class Config(object):
    LOGGER = True

    # Get this value from my.telegram.org/apps
    API_ID = 6
    API_HASH = "eb06d4abfb49dc3eeb1aeb98ae0f581e"

    CASH_API_KEY = ""  # Get this value for currency converter from https://www.alphavantage.co/support/#api-key

    DATABASE_URL = ""  # A sql database url from elephantsql.com or sqlite

    EVENT_LOGS = ()  # Event logs channel to note down important bot level events

    MONGO_DB_URI = ""  # Get this value from cloud.mongodb.com

    # Telegraph link of the image which will be shown at start command.
    START_IMG = "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=800"

    SUPPORT_CHAT = "KartikeMishra"  # Your Telegram support group chat username
    SUPPORT_CHANNEL = "AashikTeam"  # Your Telegram channel username for bot updates

    TOKEN = ""  # Get bot token from @BotFather on Telegram

    TIME_API_KEY = ""  # Get this value from https://timezonedb.com/api

    CHATBOT_API_URL = "https://chatbot.riteshyt.in/api/chat"
    CHATBOT_API_KEY = "ritesh-8179b3a5da99f300be2d50e1e9789729"

    OWNER_ID = 7163382841  # User id of your telegram account (Must be integer)

    # Optional fields
    NSFW_LOG_CHANNEL = None
    NSFW_STORAGE = None
    BL_CHATS = []  # List of groups that you want blacklisted.
    DRAGONS = []  # User id of sudo users
    DEV_USERS = []  # User id of dev users
    DEMONS = []  # User id of support users
    TIGERS = []  # User id of tiger users
    WOLVES = []  # User id of whitelist users

    ALLOW_CHATS = True
    ALLOW_EXCL = True
    DEL_CMDS = True
    INFOPIC = True
    LOAD = []
    NO_LOAD = []
    STRICT_GBAN = True
    TEMP_DOWNLOAD_DIRECTORY = "./"
    WORKERS = 8


class Production(Config):
    LOGGER = True


class Development(Config):
    LOGGER = True
