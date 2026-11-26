<!--
# Copyright (C) 2021-2026 by TheAloneTeam@Github, < https://github.com/TheAloneTeam >.
# This file is part of < https://github.com/TheAloneTeam/MeowRobot > project,
# and is released under the "MIT License Agreement".
# All rights reserved.
-->

<div align="center">

  <h1>🐾 MeowRoBot 🐾</h1>
  <p><b>Next-Generation, Modular Telegram Group Management & AI Assistant Bot</b></p>

  <p>
    <a href="https://github.com/TheAloneTeam/MeowRoBot/stargazers"><img src="https://img.shields.io/github/stars/TheAloneTeam/MeowRoBot?style=for-the-badge&logo=github&color=F59E0B" alt="Stars"/></a>
    <a href="https://github.com/TheAloneTeam/MeowRoBot/network/members"><img src="https://img.shields.io/github/forks/TheAloneTeam/MeowRoBot?style=for-the-badge&logo=github&color=6366F1" alt="Forks"/></a>
    <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.11+-38BDF8?style=for-the-badge&logo=python&logoColor=white" alt="Python Version"/></a>
    <a href="https://github.com/TheAloneTeam/MeowRoBot/blob/master/LICENSE"><img src="https://img.shields.io/badge/License-MIT-10B981?style=for-the-badge" alt="License"/></a>
    <a href="https://t.me/TeamAashik"><img src="https://img.shields.io/badge/Support-Telegram-229ED9?style=for-the-badge&logo=telegram" alt="Support Chat"/></a>
  </p>

  <img src="https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=900" width="85%" style="border-radius: 12px; margin-top: 10px;" alt="MeowRoBot Banner" />

</div>

---

## 📖 Overview

**MeowRoBot** is an enterprise-grade, lightning-fast Telegram group administration bot integrated with intelligent AI conversational capabilities. Built asynchronously on **Python 3.11+**, **Pyrogram**, and **python-telegram-bot**, it offers rock-solid moderation, granular permissions, multi-database persistence (PostgreSQL + MongoDB), and a pluggable architecture that scales effortlessly.

Whether you run a community of 50 or 500,000 members, MeowRoBot keeps your chats clean, secure, and engaging.

---

## ✨ Key Features

| Category | Highlights |
| :--- | :--- |
| 🛡️ **Group Moderation** | Automated Bans, Mutes, Kicks, Warn System, Anti-Flood, Anti-Channel, Anti-Raid, and Auto-Demote. |
| 🔒 **Comprehensive Locks** | Granular restriction on stickers, links, voice notes, documents, forwards, spoilers, commands, and bots. |
| 🤖 **Intelligent AI** | Multi-lingual conversational AI (Hinglish & English). Automatically converts long code snippets into downloadable files. |
| 🌙 **Night Mode** | Automated group lockdown during night hours with morning re-openings. |
| 📝 **Smart Notes & Filters** | Instant responses with rich media (photos, audio, videos, documents) and custom inline buttons. |
| 👥 **Community & Fun** | Daily "Couple of the Day" with custom stylized fonts, AFK status, reputation karma, and mini-games. |
| ⚡ **Dual Database Engine** | High-performance SQL (PostgreSQL / SQLite) for relational state combined with MongoDB for flexible data caching. |

---

## 🚀 One-Click Deployments

Deploy your instance in under 2 minutes:

<p align="center">
  <a href="https://dashboard.heroku.com/new?template=https://github.com/TheAloneTeam/MeowRoBot">
    <img src="https://www.herokucdn.com/deploy/button.svg" alt="Deploy to Heroku" height="38"/>
  </a>
  &nbsp;&nbsp;
  <a href="https://railway.app/new">
    <img src="https://railway.app/button.svg" alt="Deploy on Railway" height="38"/>
  </a>
  &nbsp;&nbsp;
  <a href="https://render.com">
    <img src="https://render.com/images/deploy-to-render-button.svg" alt="Deploy to Render" height="38"/>
  </a>
</p>

---

## 🛠️ Quick-Start Setup

### Method 1: Docker Compose (Recommended)

Run MeowRoBot, MongoDB, and PostgreSQL together with a single command:

```bash
# 1. Clone repository
git clone https://github.com/TheAloneTeam/MeowRoBot.git
cd MeowRoBot

# 2. Setup environment variables
cp .env.example .env
nano .env

# 3. Launch the container stack
docker compose up -d --build

# 4. View real-time logs
docker compose logs -f bot
```

---

### Method 2: Manual VPS / Local Setup

```bash
# 1. System prerequisites (Debian / Ubuntu)
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3-pip python3-venv git ffmpeg libpq-dev

# 2. Clone the repository
git clone https://github.com/TheAloneTeam/MeowRoBot.git
cd MeowRoBot

# 3. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 4. Install dependencies
pip install --upgrade pip setuptools
pip install -r requirements.txt

# 5. Configure environment variables
cp .env.example .env
nano .env

# 6. Run MeowRoBot
python3 -m MeowRobot
```

---

## ⚙️ Configuration Reference (`.env`)

| Variable | Description | Default | Required |
| :--- | :--- | :---: | :---: |
| `TOKEN` | Telegram Bot token from [@BotFather](https://t.me/BotFather) | — | **Yes** |
| `API_ID` | Telegram API ID from [my.telegram.org](https://my.telegram.org) | — | **Yes** |
| `API_HASH` | Telegram API Hash from [my.telegram.org](https://my.telegram.org) | — | **Yes** |
| `OWNER_ID` | Numeric Telegram User ID of the bot owner | — | **Yes** |
| `DATABASE_URL` | PostgreSQL or SQLite URI (`sqlite:///sqldb.db`) | `sqlite:///sqldb.db` | **Yes** |
| `MONGO_DB_URI` | MongoDB Connection String (`mongodb://...`) | — | **Yes** |
| `SUPPORT_CHAT` | Username of your Telegram support group | `TeamAashik` | No |
| `SUPPORT_CHANNEL` | Username of your Telegram news/updates channel | `AashikTeam` | No |
| `CHATBOT_API_URL` | AI Chatbot endpoint | Default API | No |
| `CHATBOT_API_KEY` | Optional authorization key for AI Chatbot | — | No |
| `EVENT_LOGS` | Telegram channel ID for system event logging | — | No |
| `WORKERS` | Max concurrent worker threads | `8` | No |

---

## 📂 Repository Structure

```text
MeowRoBot/
├── .github/                      # Issue & PR templates, CI workflows
├── MeowRobot/
│   ├── config.py                 # Clean configuration loader
│   ├── events.py                 # Event decorators & handlers
│   ├── modules/                  # 90+ Pluggable features
│   │   ├── helper_funcs/         # Permissions, filters, extraction utilities
│   │   └── sql/                  # SQLAlchemy ORM database models
│   ├── resources/                # Fonts, assets, default banners
│   └── utils/                    # MongoDB handlers, rate limiters, formatters
├── .env.example                  # Environment configuration template
├── docker-compose.yml            # Turnkey multi-container orchestration
├── Dockerfile                    # Container build manifest
├── requirements.txt              # Production Python dependencies
└── README.md                     # Project documentation
```

---

## 🤝 Contributing

Contributions are what make the open-source community an inspiring place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'feat: Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

Please review our [Contributing Guidelines](.github/CONTRIBUTING.md) and [Code of Conduct](.github/CODE_OF_CONDUCT.md).

---

## 📈 Star History

<p align="center">
  <a href="https://star-history.com/#TheAloneTeam/MeowRoBot&Date">
    <img src="https://api.star-history.com/svg?repos=TheAloneTeam/MeowRoBot&type=Date" alt="Star History Chart" width="700"/>
  </a>
</p>

---

## 📜 License & Acknowledgments

This project is licensed under the **[MIT License](LICENSE)**.

- **[TheAloneTeam](https://github.com/TheAloneTeam)** — Maintainer & Lead Developer
- **[Paul Larsen](https://github.com/PaulSonOfLars)** — Base framework concept
- **[Hamker Cat](https://github.com/TheHamkerCat)** — Modular architectural inspiration
- Thanks to all contributors and community members!
