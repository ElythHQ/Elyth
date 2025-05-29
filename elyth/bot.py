import discord
from discord.ext import commands
import shlex
import asyncio
import traceback 

from .context import ElythContext
from .action_executor import ActionExecutor

class ElythBot: 
    def __init__(self, token: str, prefix: str | list[str] = "!", intents: discord.Intents | None = None, **options):
        if intents is None:
            intents = discord.Intents.default()
            intents.message_content = True
            intents.members = True
            intents.guilds = True
        self.token = token
        self.prefix = prefix
        self._intents = intents
        self.dpy_bot = commands.Bot(command_prefix=self._get_prefix_callable(), intents=intents, help_command=None, **options)
        self._elyth_commands = {}
        self._elyth_event_handlers = {}
        self.action_executor = ActionExecutor(self)
        self._register_discord_events()

    def _get_prefix_list(self) -> list[str]:
        return [self.prefix] if isinstance(self.prefix, str) else self.prefix

    def _get_prefix_callable(self):
        async def get_actual_prefix(bot, message):
            return commands.when_mentioned_or(*self._get_prefix_list())(bot, message)
        return get_actual_prefix

    def _register_discord_events(self):
        @self.dpy_bot.event
        async def on_ready():
            if "on_ready" in self._elyth_event_handlers:
                ctx = ElythContext(bot_instance=self, event_data={'event_name': 'on_ready'})
                await self.action_executor.execute_actions(self._elyth_event_handlers["on_ready"], ctx)
            else:
                print(f"--------------------------------------------------")
                print(f"Logged in as: {self.dpy_bot.user.name} ({self.dpy_bot.user.id})")
                print(f"ElythBot (Simplicity Model) is ready!")
                prefixes = self._get_prefix_list()
                print(f"Listening for prefix(es): {', '.join(prefixes)}")
                if self.dpy_bot.user and (self.dpy_bot.user.mention in prefixes or f"<@!{self.dpy_bot.user.id}>" in prefixes):
                     print(f"Also responds to @mentions as prefix.")
                print(f"--------------------------------------------------")

        @self.dpy_bot.event
        async def on_message(message: discord.Message):
            if message.author.bot:
                if "on_bot_message" in self._elyth_event_handlers:
                    ctx = ElythContext(bot_instance=self, message=message, event_data={'event_name': 'on_bot_message'})
                    await self.action_executor.execute_actions(self._elyth_event_handlers["on_bot_message"], ctx)
                return
            if "on_message" in self._elyth_event_handlers:
                ctx = ElythContext(bot_instance=self, message=message, event_data={'event_name': 'on_message'})
                await self.action_executor.execute_actions(self._elyth_event_handlers["on_message"], ctx)
            actual_prefix_used = None
            content_for_command_check = message.content
            if self.dpy_bot.user:
                mention_plain, mention_nick = f"<@{self.dpy_bot.user.id}>", f"<@!{self.dpy_bot.user.id}>"
                if content_for_command_check.startswith(mention_plain): actual_prefix_used = mention_plain
                elif content_for_command_check.startswith(mention_nick): actual_prefix_used = mention_nick
            if not actual_prefix_used:
                for pfx in self._get_prefix_list():
                    if content_for_command_check.startswith(pfx):
                        actual_prefix_used = pfx; break
            if not actual_prefix_used: return
            content_without_prefix = content_for_command_check[len(actual_prefix_used):].lstrip()
            if not content_without_prefix: return
            try:
                command_parts = shlex.split(content_without_prefix)
                command_trigger, command_args = command_parts[0].lower(), command_parts[1:]
            except ValueError: return
            if command_trigger in self._elyth_commands:
                actions_to_run = self._elyth_commands[command_trigger]
                ctx = ElythContext(bot_instance=self, message=message, args=command_args)
                try: await self.action_executor.execute_actions(actions_to_run, ctx)
                except discord.Forbidden:
                    try: await message.channel.send(f":no_entry_sign: I don't have permission for `{command_trigger}`.")
                    except: pass
                except Exception as e:
                    print(f"Error in Elyth command '{command_trigger}' for {message.author}: {e}")
                    traceback.print_exc()
                    try: await message.channel.send(f":warning: Oops! Error with `{command_trigger}`.")
                    except: pass

        all_discord_event_names = [attr for attr in dir(discord.Client) if attr.startswith('on_')]
        for event_name_dpy in all_discord_event_names:
            if event_name_dpy in ["on_ready", "on_message"]: continue
            def create_generic_handler(captured_event_name):
                async def generic_event_handler(*args, **kwargs):
                    if captured_event_name in self._elyth_event_handlers:
                        event_data = {'event_name': captured_event_name, 'raw_args': args, 'raw_kwargs': kwargs}
                        msg_obj, member_obj, user_obj, guild_obj, channel_obj = None, None, None, None, None
                        for arg_val in args:
                            if isinstance(arg_val, discord.Message) and not msg_obj: msg_obj = arg_val
                            elif isinstance(arg_val, discord.Member) and not member_obj: member_obj, user_obj = arg_val, arg_val
                            elif isinstance(arg_val, discord.User) and not user_obj: user_obj = arg_val
                            elif isinstance(arg_val, discord.Guild) and not guild_obj: guild_obj = arg_val
                            elif isinstance(arg_val, discord.abc.GuildChannel) and not channel_obj: channel_obj = arg_val
                            elif isinstance(arg_val, discord.DMChannel) and not channel_obj: channel_obj = arg_val
                        if captured_event_name in ["on_member_join", "on_member_remove", "on_member_update", "on_voice_state_update"]:
                            if args and isinstance(args[0], (discord.Member, discord.User)): event_data['member'] = args[0]
                            if captured_event_name in ["on_member_update", "on_voice_state_update"] and len(args)>1 and isinstance(args[1], (discord.Member, discord.User, discord.VoiceState)): event_data['after_state_or_member'] = args[1]
                        elif captured_event_name in ["on_reaction_add", "on_reaction_remove"]:
                            if args and isinstance(args[0], discord.Reaction): event_data['reaction'] = args[0]
                            if len(args)>1 and isinstance(args[1], (discord.Member, discord.User)): event_data['user'] = args[1]
                        elif captured_event_name == "on_message_delete": # Example for specific event
                            if args and isinstance(args[0], discord.Message): event_data['message'] = args[0] # The deleted message


                        ctx = ElythContext(bot_instance=self, message=msg_obj, event_data=event_data)
                        if member_obj and not ctx.author: ctx.author = member_obj
                        if user_obj and not ctx.author: ctx.author = user_obj
                        if guild_obj and not ctx.guild: ctx.guild = guild_obj
                        if channel_obj and not ctx.channel: ctx.channel = channel_obj
                        await self.action_executor.execute_actions(self._elyth_event_handlers[captured_event_name], ctx)
                return generic_event_handler
            try:
                if hasattr(self.dpy_bot, event_name_dpy) and asyncio.iscoroutinefunction(getattr(self.dpy_bot, event_name_dpy, None)):
                     self.dpy_bot.add_listener(create_generic_handler(event_name_dpy), event_name_dpy)
            except Exception as e: print(f"ElythBot: Minor issue registering generic listener for {event_name_dpy}: {e}")

    def command(self, trigger: str, actions: str | list[str]):
        processed_trigger = trigger.lower().strip()
        if not processed_trigger: print("Elyth Error: Command trigger cannot be empty."); return
        if ' ' in processed_trigger:
            first_word = processed_trigger.split()[0]
            print(f"Elyth Warning: Command trigger '{trigger}' contains spaces. Using first word '{first_word}'.")
            processed_trigger = first_word
        if processed_trigger in self._elyth_commands: print(f"Elyth Warning: Command trigger '{processed_trigger}' is being redefined.")
        self._elyth_commands[processed_trigger] = actions

    def event(self, event_name: str, actions: str | list[str]):
        processed_event_name = event_name.lower().strip()
        if not processed_event_name.startswith("on_"): processed_event_name = f"on_{processed_event_name}"
        self._elyth_event_handlers[processed_event_name] = actions

    @property
    def user(self): return self.dpy_bot.user if self.dpy_bot.user else None

    def run(self):
        if not self.token: raise ValueError("ElythBot: Bot token is not set.")
        if not self._elyth_commands and not self._elyth_event_handlers:
            print("Elyth Warning: No commands or event handlers defined. The bot will connect but do nothing else.")
        print(f"Elyth: {len(self._elyth_commands)} commands loaded.")
        print(f"Elyth: {len(self._elyth_event_handlers)} event actions loaded for: {list(self._elyth_event_handlers.keys())}")
        try: self.dpy_bot.run(self.token)
        except discord.LoginFailure: print("ElythBot Error: Improper token has been passed.")
        except discord.PrivilegedIntentsRequired as e:
            print(f"ElythBot Error: Privileged intents are required but not enabled: {e}")
            print("Please enable Server Members Intent and Message Content Intent in your bot's settings on the Discord Developer Portal.")
        except Exception as e:
            print(f"ElythBot Error: An unexpected error occurred: {e}")
            traceback.print_exc()