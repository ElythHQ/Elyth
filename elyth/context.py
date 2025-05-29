import discord
import random 
from datetime import datetime 


class ElythContext:
    def __init__(self, bot_instance, message: discord.Message | None = None, event_data: dict | None = None, args: list[str] | None = None):
        self._bot = bot_instance 
        self.message = message    
        self.event_data = event_data if event_data else {} 
        self.args = args if args else [] 

        self.author: discord.User | discord.Member | None = None
        self.channel: discord.abc.Messageable | None = None
        self.guild: discord.Guild | None = None

        if message:
            self.author = message.author
            self.channel = message.channel
            self.guild = message.guild
        elif 'member' in self.event_data and isinstance(self.event_data['member'], (discord.Member, discord.User)):
            self.author = self.event_data['member']
            self.guild = self.event_data['member'].guild if isinstance(self.event_data['member'], discord.Member) else None
        elif 'user' in self.event_data and isinstance(self.event_data['user'], discord.User):
            self.author = self.event_data['user']

        if not self.channel:
            if 'channel' in self.event_data and isinstance(self.event_data['channel'], discord.abc.Messageable):
                self.channel = self.event_data['channel']
            elif self.guild and 'channel_id' in self.event_data:
                try:
                    fetched_channel = self.guild.get_channel(int(self.event_data['channel_id']))
                    if isinstance(fetched_channel, discord.abc.Messageable):
                        self.channel = fetched_channel
                except (ValueError, TypeError):
                    pass

        if not self.guild:
            if 'guild' in self.event_data and isinstance(self.event_data['guild'], discord.Guild):
                self.guild = self.event_data['guild']
            elif self.channel and hasattr(self.channel, 'guild'):
                self.guild = self.channel.guild


    def _get_variable_value(self, var_full: str) -> str:
        var_key = var_full.lower()
        if self.message:
            if var_key == "message.content": return str(self.message.content)
            if var_key == "message.id": return str(self.message.id)
            if var_key == "message.channel.id": return str(self.message.channel.id)
            if var_key == "message.channel.name": return str(getattr(self.message.channel, 'name', 'DM'))
            if var_key == "message.author.name": return str(self.message.author.name)
        if self.author:
            if var_key in ["user.name", "author.name"]: return str(self.author.name)
            if var_key in ["user.id", "author.id"]: return str(self.author.id)
            if var_key in ["user.mention", "author.mention"]: return self.author.mention
            if var_key in ["user.discriminator", "author.discriminator"]: return str(self.author.discriminator)
            if var_key == "user.avatar_url": return str(self.author.display_avatar.url)
            if isinstance(self.author, discord.Member):
                if var_key in ["user.nick", "author.nick"]: return str(self.author.nick or self.author.name)
                if var_key in ["user.display_name", "author.display_name"]: return str(self.author.display_name)
                if var_key == "user.roles_names": return ", ".join(role.name for role in self.author.roles if role.name != "@everyone")
                if var_key == "user.top_role_name": return str(self.author.top_role.name)
        if self.channel:
            if var_key == "channel.id": return str(self.channel.id)
            if var_key == "channel.name": return str(getattr(self.channel, 'name', 'DM Channel'))
            if var_key == "channel.mention" and hasattr(self.channel, 'mention'): return self.channel.mention
        if self.guild:
            if var_key in ["server.name", "guild.name"]: return str(self.guild.name)
            if var_key in ["server.id", "guild.id"]: return str(self.guild.id)
            if var_key in ["server.member_count", "guild.member_count"]: return str(self.guild.member_count)
            if var_key == "server.icon_url": return str(self.guild.icon.url if self.guild.icon else "")
            if var_key == "server.owner.id": return str(self.guild.owner_id)
            if var_key == "server.owner.name":
                owner = self.guild.owner
                return str(owner.name if owner else "Unknown Owner")
        if var_key.startswith("arg[") and var_key.endswith("]"):
            try:
                index = int(var_key[4:-1]) - 1
                return str(self.args[index]) if 0 <= index < len(self.args) else ""
            except (ValueError, IndexError): return ""
        if var_key.startswith("$") and var_key[1:].isdigit():
            try:
                index = int(var_key[1:]) - 1
                return str(self.args[index]) if 0 <= index < len(self.args) else ""
            except (ValueError, IndexError): return ""
        if var_key == "args": return " ".join(self.args)
        if var_key in ["argslen", "argscount"]: return str(len(self.args))
        bot_user = self._bot.dpy_bot.user
        if bot_user:
            if var_key == "bot.name": return str(bot_user.name)
            if var_key == "bot.id": return str(bot_user.id)
            if var_key == "bot.mention": return bot_user.mention
        if var_key == "bot.prefix":
            p = self._bot.prefix
            return p[0] if isinstance(p, list) else str(p)
        if var_key == "bot.latency_ms": return f"{self._bot.dpy_bot.latency * 1000:.0f}"
        if var_key.startswith("random["):
            content = var_key[7:-1]
            parts = [p.strip() for p in content.split(',')]
            if len(parts) == 2:
                try:
                    min_val, max_val = int(parts[0]), int(parts[1])
                    return str(random.randint(min_val, max_val))
                except ValueError: return random.choice(parts) if parts else ""
            elif len(parts) > 0: return random.choice(parts)
            return ""
        if var_key == "time": return datetime.now().strftime("%H:%M:%S")
        if var_key == "date": return datetime.now().strftime("%Y-%m-%d")
        if var_key == "timestamp": return str(int(datetime.now().timestamp()))
        if var_key.startswith("roleid[") and var_key.endswith("]") and self.guild:
            role_name_query = var_key[7:-1]
            found_role = discord.utils.get(self.guild.roles, name=role_name_query)
            return str(found_role.id) if found_role else f"ROLE_ID_NOT_FOUND:{role_name_query}"
        if var_key.startswith("channelid[") and var_key.endswith("]") and self.guild:
            channel_name_query = var_key[10:-1]
            found_channel = discord.utils.get(self.guild.text_channels, name=channel_name_query)
            return str(found_channel.id) if found_channel else f"CHANNEL_ID_NOT_FOUND:{channel_name_query}"
        if var_key.startswith("userid[") and var_key.endswith("]") and self.guild:
            user_name_query = var_key[7:-1]
            found_member = discord.utils.get(self.guild.members, name=user_name_query)
            if not found_member and '#' in user_name_query:
                name_part, discrim_part = user_name_query.rsplit('#', 1)
                found_member = discord.utils.get(self.guild.members, name=name_part, discriminator=discrim_part)
            return str(found_member.id) if found_member else f"USER_ID_NOT_FOUND:{user_name_query}"
        if var_key.startswith("event."):
            event_data_key = var_key[len("event."):]
            if event_data_key in self.event_data: return str(self.event_data[event_data_key])
            else:
                if 'raw_args' in self.event_data and event_data_key.isdigit():
                    idx = int(event_data_key)
                    if 0 <= idx < len(self.event_data['raw_args']): return str(self.event_data['raw_args'][idx])
                return f"EVENT_DATA_KEY_NOT_FOUND:{event_data_key}"
        return "{" + var_full + "}"

    def process_string_variables(self, text: str) -> str:
        import re
        def replace_match(match): return self._get_variable_value(match.group(1))
        processed_text = text
        for _ in range(5):
            new_text = re.sub(r"\{([\w.\[\]$:\-]+(?:\[[^\]]+\])?)\}", replace_match, processed_text)
            if new_text == processed_text: break
            processed_text = new_text
        return processed_text

    async def _reply(self, content: str, mention_author: bool = False):
        if self.message and self.channel and isinstance(self.channel, discord.abc.Messageable):
            processed_content = self.process_string_variables(content)
            try: await self.message.reply(processed_content, mention_author=mention_author)
            except discord.HTTPException as e:
                print(f"Error during _reply: {e}")
                try: await self.channel.send(f"(Reply to {self.author.mention} failed) {processed_content}")
                except Exception as e2: print(f"Error during _reply fallback send: {e2}")
        else: print(f"ElythContext: Cannot reply, no message/channel context or channel not messageable. Content: {content[:50]}...")

    async def _send(self, target_channel_id_or_name: str | None, content: str):
        processed_content = self.process_string_variables(content)
        final_target_channel = None
        if target_channel_id_or_name:
            processed_target_id_or_name = self.process_string_variables(target_channel_id_or_name)
            try:
                chan_id = int(processed_target_id_or_name)
                found_chan = self._bot.dpy_bot.get_channel(chan_id)
                if found_chan and isinstance(found_chan, discord.abc.Messageable): final_target_channel = found_chan
            except ValueError:
                if self.guild:
                    found_chan_by_name = discord.utils.get(self.guild.text_channels, name=processed_target_id_or_name)
                    if not found_chan_by_name: found_chan_by_name = discord.utils.get(self.guild.voice_channels, name=processed_target_id_or_name)
                    if found_chan_by_name and isinstance(found_chan_by_name, discord.abc.Messageable): final_target_channel = found_chan_by_name
        if not final_target_channel:
            if self.channel and isinstance(self.channel, discord.abc.Messageable): final_target_channel = self.channel
            else:
                print(f"ElythContext: No valid channel to send message. Target: '{target_channel_id_or_name}', Current: '{getattr(self.channel, 'name', 'None')}'. Content: {content[:50]}...")
                return
        try: await final_target_channel.send(processed_content)
        except discord.Forbidden: print(f"ElythContext: Forbidden to send message to {getattr(final_target_channel, 'name', final_target_channel.id)}. Check bot permissions.")
        except discord.HTTPException as e: print(f"Error during _send to {getattr(final_target_channel, 'name', final_target_channel.id)}: {e}")

    async def _add_role(self, user_identifier: str, role_identifier: str, reason: str | None = None):
        if not self.guild:
            await self._reply("Error: This action can only be performed in a server.")
            return
        user_id_str = self.process_string_variables(user_identifier)
        role_id_or_name_str = self.process_string_variables(role_identifier)
        processed_reason = self.process_string_variables(reason) if reason else f"Action by {self._bot.dpy_bot.user.name}"
        member: discord.Member | None = None
        role_to_add: discord.Role | None = None
        try:
            member_id = int(user_id_str)
            member = self.guild.get_member(member_id)
            if not member: member = await self.guild.fetch_member(member_id)
        except (ValueError, discord.NotFound):
            member = discord.utils.get(self.guild.members, name=user_id_str)
            if not member and '#' in user_id_str:
                name_part, discrim_part = user_id_str.rsplit('#', 1)
                member = discord.utils.get(self.guild.members, name=name_part, discriminator=discrim_part)
        except discord.HTTPException as e:
            await self._reply(f"Error fetching member '{user_id_str}': {e}")
            return
        if not member:
            await self._reply(f"Error: Could not find member: `{user_identifier}` (resolved to `{user_id_str}`).")
            return
        try:
            role_id = int(role_id_or_name_str)
            role_to_add = self.guild.get_role(role_id)
        except ValueError: role_to_add = discord.utils.get(self.guild.roles, name=role_id_or_name_str)
        if not role_to_add:
            await self._reply(f"Error: Could not find role: `{role_identifier}` (resolved to `{role_id_or_name_str}`).")
            return
        try:
            await member.add_roles(role_to_add, reason=processed_reason)
            await self._reply(f"Successfully added role '{role_to_add.name}' to {member.mention}.")
        except discord.Forbidden: await self._reply(f"Error: I don't have permission to add role '{role_to_add.name}' to {member.mention}. My top role might be below the target role or I lack 'Manage Roles' permission.")
        except discord.HTTPException as e: await self._reply(f"Error adding role: {e}")

    async def _print(self, message: str):
        processed_message = self.process_string_variables(message)
        print(f"[Elyth PRINT Action] {processed_message}")