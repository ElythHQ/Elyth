<p align="center">
  <img src="https://raw.githubusercontent.com/ElythHQ/Elyth/main/elyth_logo.svg" alt="Elyth Logo" width="250"/>
</p>


# Elyth 📦

**Elyth: Create Discord bots in Python with dead-simple, string-based commands!**

Inspired by the ease-of-use of tools like Botforge and Aoi.js, Elyth aims to make Discord bot development in Python accessible to everyone, even with minimal Python knowledge. Focus on *what* your bot should do, not complex boilerplate.

[![PyPI version](https://badge.fury.io/py/elyth.svg)](https://badge.fury.io/py/elyth)
[![Python Version](https://img.shields.io/pypi/pyversions/elyth.svg)](https://pypi.org/project/elyth/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/ElythHQ/Elyth/blob/main/LICENSE)
[![GitHub issues](https://img.shields.io/github/issues/ElythHQ/Elyth)](https://github.com/ElythHQ/Elyth/issues)
[![Discord](https://img.shields.io/discord/1056887212207259668?label=discord&logo=discord)](https://discord.gg/KN8qZh5c98)

## ✨ Features

*   **Ultra-Simple Syntax:** Define bot commands and event responses using intuitive strings.
*   **Powerful Variable System:** Easily access information like `{user.name}`, `{args}`, `{channel.id}`, `{server.member_count}`, `{random[1,10]}` and more within your action strings.
*   **Minimal Python Overhead:** Write less Python, build more bot!
*   **Extensible:** Built on the robust `discord.py` library.
*   **Beginner-Friendly:** Perfect for those new to Python or bot development.

## 🚀 Quick Start

1.  **Installation:**
    ```bash
    pip install elyth
    ```
    *(Requires Python 3.8+)*

2.  **Get a Discord Bot Token:**
    *   Go to the [Discord Developer Portal](https://discord.com/developers/applications).
    *   Create a "New Application" and then a "Bot" user for it.
    *   Copy the **Bot Token**.
    *   Enable **Privileged Gateway Intents** for your bot:
        *   `SERVER MEMBERS INTENT`
        *   `MESSAGE CONTENT INTENT`
        *   `GUILDS` (Generally recommended)

3.  **Create your bot file (e.g., `my_bot.py`):**
    ```python
    from elyth import ElythBot
    import os

    TOKEN = os.getenv("DISCORD_BOT_TOKEN")

    if not TOKEN:
        print("Error: DISCORD_BOT_TOKEN environment variable not set!")
        exit()

    bot = ElythBot(token=TOKEN, prefix="e!")

    bot.command("hello", "REPLY: Hello there, {user.mention}! I am {bot.name}, powered by Elyth!")
    bot.command("ping", "SAY: Pong! My current latency to Discord is {bot.latency_ms}ms.")
    bot.command("info", [
        "REPLY: You are {user.display_name} (`{user.id}`)",
        "SAY: This command was used in channel #{channel.name} on the server '{server.name}'."
    ])
    bot.command("echo", "SAY: You wanted me to say: {args}") 

    bot.event("on_ready", "PRINT: Elyth bot ({bot.name}) is connected and ready with prefix '{bot.prefix}'!")
    bot.event("member_join", "SEND #general: Everyone say hello to {user.mention}, our newest member of {server.name}! 🎉")

    bot.run()
    ```

4.  **Run your bot:**
    ```bash
    python my_bot.py
    ```

## 💡 Future Ideas & Roadmap

*   More Action Verbs (Kick, Ban, Embeds, Reactions, Set Activity, etc.)
*   Conditional logic in action strings (`IF ... THEN ... ELSE ...`)
*   Support for Slash Commands
*   Support for UI Components (Buttons, Select Menus)
*   User-defined variables/functions within the Elyth syntax
*   Enhanced error handling and feedback

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Please feel free to:
*   [Open an issue](https://github.com/ElythHQ/Elyth/issues) for bugs or feature suggestions.
*   Fork the repository and submit a pull request for enhancements.

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/ElythHQ/Elyth/blob/main/LICENSE) file for details.

---

*Elyth is lovingly crafted by* [Golgrax (Karl Benjamin R. Bughaw](https://github.com/Golgrax) */* [ElythHQ](https://github.com/ElythHQ).
