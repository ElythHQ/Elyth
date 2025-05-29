# Elyth 📦 <img src="https://raw.githubusercontent.com/ElythHQ/Elyth/main/assets/elyth_logo.svg" alt="Elyth Logo" width="50"/>

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

## 📚 Documentation

Elyth simplifies bot creation through **Action Strings**. An action string typically consists of a `VERB` followed by arguments and can utilize dynamic `{variables}`.

### Common Action Verbs (Version 0.0.0.2)

*   `REPLY: <message>`
    *   Replies to the command-issuing message.
    *   Mentions the user by default.
    *   Example: `REPLY: Got it, {user.nick}!`
*   `SAY: <message>`
    *   Sends a message to the current channel.
    *   Does *not* mention the triggering user by default.
    *   Example: `SAY: The current time is {time}.`
*   `SEND <#channel_name_or_id_or_var>: <message>`
    *   Sends a message to a specific channel.
    *   Target can be a channel name (e.g., `#announcements`), a channel ID (e.g., `1234567890`), or a variable resolving to one (e.g., `{channel.id}`).
    *   Example: `SEND #logs: User {user.name} used the {message.content.split()[0]} command.`
*   `ADDROLE <user_id_or_mention_or_name_or_var> <role_id_or_name_or_var>: [optional_reason]`
    *   Adds a role to a user. Bot needs "Manage Roles" permission and its highest role must be above the role being added.
    *   User/Role can be ID, name, @mention (for user), or a variable.
    *   Example: `ADDROLE {user.id} {roleID[Verified]}: User verified.`
*   `PRINT: <message>`
    *   Prints a message to the bot's console. Useful for `on_ready` or debugging.
    *   Example: `PRINT: Bot initialization sequence complete at {timestamp}.`

*(More verbs are planned for future versions!)*

### Available Variables (Version 0.0.0.2 - Examples)

This is not an exhaustive list. Variables provide dynamic data within your action strings.

**User/Author Context (typically the user who triggered the command/event):**
*   `{user.name}`: Username (e.g., `CoolUser`)
*   `{user.id}`: User's unique ID (e.g., `123456789012345678`)
*   `{user.mention}`: Creates an @mention for the user.
*   `{user.discriminator}`: User's 4-digit tag (e.g., `1234`). (Note: This is becoming less common with Discord's new username system).
*   `{user.nick}`: User's server nickname (falls back to username if no nickname).
*   `{user.display_name}`: User's display name on the server (nickname or username).
*   `{user.avatar_url}`: URL of the user's avatar.
*   `{user.roles_names}`: Comma-separated list of the user's role names (excluding @everyone).
*   `{user.top_role_name}`: Name of the user's highest role on the server.

**Message Context (for commands triggered by messages):**
*   `{message.content}`: The full content of the message that triggered the command.
*   `{message.id}`: The ID of the triggering message.

**Command Argument Variables:**
*   `{args}`: All text that comes after the command trigger. (e.g., in `e!say Hello World`, `{args}` is `Hello World`).
*   `{arg[1]}`, `{arg[2]}`, ... `{arg[N]}`: The Nth argument (word) after the command trigger. (e.g., in `e!greet David`, `{arg[1]}` is `David`).
*   `{argslen}` or `{argscount}`: The number of arguments provided.

**Channel Context (where the command was used or event occurred):**
*   `{channel.name}`: Name of the current channel (e.g., `general`, or `DM Channel` for DMs).
*   `{channel.id}`: ID of the current channel.
*   `{channel.mention}`: Creates a #mention for the channel.

**Server/Guild Context (if applicable):**
*   `{server.name}` or `{guild.name}`: Name of the server.
*   `{server.id}` or `{guild.id}`: ID of the server.
*   `{server.member_count}` or `{guild.member_count}`: Total number of members in the server.
*   `{server.icon_url}`: URL of the server's icon (if any).
*   `{server.owner.id}`: ID of the server owner.
*   `{server.owner.name}`: Name of the server owner.

**Bot Information:**
*   `{bot.name}`: The bot's username.
*   `{bot.id}`: The bot's ID.
*   `{bot.mention}`: Creates an @mention for the bot.
*   `{bot.prefix}`: The primary prefix the bot is configured with.
*   `{bot.latency_ms}`: The bot's network latency to Discord in milliseconds.

**Utility Variables:**
*   `{random[min,max]}`: A random integer between min and max (inclusive). Example: `{random[1,100]}`.
*   `{random[choice1,choice2,...]}`: A random choice from the provided list. Example: `{random[Red,Green,Blue]}`.
*   `{time}`: Current time in HH:MM:SS format.
*   `{date}`: Current date in YYYY-MM-DD format.
*   `{timestamp}`: Current Unix timestamp (seconds since epoch).

**ID Lookup Variables (require server context):**
*   `{roleID[RoleName]}`: Tries to find a role named "RoleName" and returns its ID.
*   `{channelID[channel-name]}`: Tries to find a text channel named "channel-name" and returns its ID.
*   `{userID[Username]}` or `{userID[Username#1234]}`: Tries to find a user by name (or name+tag) and returns their ID.
    *   *Note: User lookups by name can be unreliable with Discord's new username system. ID or mention is preferred for targeting users.*

**Event-Specific Data (using `{event.key}`):**
*   For events not directly tied to a message (e.g., `on_member_join`, `on_message_delete`), data specific to that event can often be accessed via `{event.some_property}`.
*   Example for `on_message_delete`:
    *   `{event.message.content}`: Content of the deleted message.
    *   `{event.message.author.name}`: Author of the deleted message.
*   *(The exact available `event.*` variables depend on the event. Check the `ElythContext` `event_data` population in `bot.py` for advanced insight or future detailed event docs.)*

*(This list will be expanded as Elyth grows! For the most up-to-date list, please refer to the [source code](https://github.com/ElythHQ/Elyth/blob/main/elyth/context.py) or future dedicated documentation.)*

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
