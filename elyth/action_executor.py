import shlex

class ActionExecutor:
    def __init__(self, bot_instance):
        self._bot = bot_instance

    async def execute_actions(self, action_definitions: str | list[str], context): # context is ElythContext
        if isinstance(action_definitions, str):
            action_definitions = [action_definitions]
        for action_def_raw in action_definitions:
            if not action_def_raw.strip(): continue
            verb, args_string = "", ""
            action_def_processed_vars = context.process_string_variables(action_def_raw)
            split_by_colon = action_def_processed_vars.split(":", 1)
            if len(split_by_colon) > 1:
                verb = split_by_colon[0].strip().upper()
                args_string = split_by_colon[1].strip()
            else:
                try:
                    temp_parts = shlex.split(action_def_processed_vars)
                    if temp_parts:
                        verb = temp_parts[0].upper()
                        args_string = action_def_processed_vars[len(temp_parts[0]):].strip()
                except ValueError: pass
            if not verb:
                await context._reply(action_def_processed_vars)
                continue
            if verb == "REPLY": await context._reply(args_string)
            elif verb == "SAY": await context._reply(args_string, mention_author=False)
            elif verb == "SEND" or verb == "SENDMESSAGE":
                send_parts = []
                try: send_parts = shlex.split(args_string)
                except ValueError:
                    print(f"Elyth ActionExecutor: Error parsing SEND arguments: {args_string}")
                    if context.message: await context._reply(f":warning: Error in SEND arguments: `{args_string}`")
                    continue
                if not send_parts:
                    if context.message: await context._reply(f":warning: {verb} action needs a message.")
                    continue
                target_channel_str, message_content_str = None, ""
                is_potential_channel = (send_parts[0].isdigit() or send_parts[0].startswith(("<#", "#")) or (send_parts[0].startswith("{") and send_parts[0].endswith("}")))
                if is_potential_channel and len(send_parts) > 1:
                    target_channel_str = send_parts[0]
                    message_content_str = " ".join(send_parts[1:])
                else: message_content_str = args_string
                await context._send(target_channel_str, message_content_str)
            elif verb == "ADDROLE":
                addrole_parts = []
                try: addrole_parts = shlex.split(args_string)
                except ValueError:
                    print(f"Elyth ActionExecutor: Error parsing ADDROLE arguments: {args_string}")
                    if context.message: await context._reply(f":warning: Error in ADDROLE arguments: `{args_string}`")
                    continue
                if len(addrole_parts) < 2:
                    if context.message: await context._reply(f":warning: ADDROLE needs user and role. Format: `ADDROLE <user> <role> [reason]`")
                    continue
                user_str, role_str = addrole_parts[0], addrole_parts[1]
                reason_str = " ".join(addrole_parts[2:]) if len(addrole_parts) > 2 else None
                await context._add_role(user_str, role_str, reason_str)
            elif verb == "PRINT": await context._print(args_string)
            else:
                print(f"Elyth ActionExecutor: Unknown action verb '{verb}' in '{action_def_raw}'. Treating as implicit reply.")
                await context._reply(action_def_raw)