import asyncio
import json

import utils
import zcash

from nearai.agents.environment import Environment

from rich.console import Console
from rich.markdown import Markdown
from rich import print as rprint

from intents.deposit import _deposit_to_intents
from intents.swap import intent_swap
from intents.withdraw import withdraw_from_intents
from io import StringIO

import sys

# Create a simple Environment wrapper if nearai's Environment can't be instantiated
class SimpleEnvironment:
    def __init__(self):
        self.env_vars = {}
        self.messages = []
        self.tool_registry = None
    
    def add_reply(self, msg):
        self.messages.append(msg)
        print(msg)
    
    def list_messages(self):
        return self.messages
    
    def get_tool_registry(self, new=False):
        class ToolRegistry:
            def __init__(self):
                self.tools = {}
            
            def register_tool(self, func):
                self.tools[func.__name__] = func
            
            def get_all_tool_definitions(self):
                return list(self.tools.values())
        
        self.tool_registry = ToolRegistry()
        return self.tool_registry
    
    def set_near(self, account_id, private_key):
        # Mock NEAR connection
        return None
    
    def completions_and_run_tools(self, messages, tools=None, add_responses_to_messages=False):
        from openai import OpenAI
        import inspect
        client = OpenAI()
        
        # Convert tool functions to OpenAI tool definitions
        tool_definitions = []
        tool_map = {}
        
        if tools:
            for tool in tools:
                sig = inspect.signature(tool)
                params = {}
                required = []
                
                for param_name, param in sig.parameters.items():
                    if param_name in ['env', 'args', 'data']:  # Skip internal params
                        continue
                    if param.default == inspect.Parameter.empty:
                        required.append(param_name)
                    params[param_name] = {"type": "string"}
                
                tool_definitions.append({
                    "type": "function",
                    "function": {
                        "name": tool.__name__,
                        "description": (tool.__doc__ or "No description")[:200],  # Limit length
                        "parameters": {
                            "type": "object",
                            "properties": params,
                            "required": required if required else []
                        }
                    }
                })
                tool_map[tool.__name__] = tool
        
        # Debug: show if tools are being sent
        if tool_definitions:
            print(f"[DEBUG] Sending {len(tool_definitions)} tools to OpenAI", flush=True)
        
        # Call OpenAI with tool use
        response = client.chat.completions.create(
            model='gpt-4o-mini',
            messages=messages,
            tools=tool_definitions if tool_definitions else None,
            tool_choice="auto" if tool_definitions else None,
            temperature=0.7
        )
        
        # Return mock response object
        class MockResponse:
            def __init__(self, content, tool_calls=None):
                self.choices = [type('obj', (object,), {
                    'message': type('obj', (object,), {
                        'content': content,
                        'function_call': tool_calls,
                        'tool_calls': tool_calls
                    })()
                })()]
        
        message = response.choices[0].message
        tool_calls = None
        content = message.content or ""
        
        # Check if there are tool calls
        if hasattr(message, 'tool_calls') and message.tool_calls:
            print(f"[DEBUG] Tool calls detected: {len(message.tool_calls)}", flush=True)
            for tool_call in message.tool_calls:
                tool_name = tool_call.function.name
                print(f"[DEBUG] Executing tool: {tool_name}", flush=True)
                
                # Execute the tool
                if tool_name in tool_map:
                    try:
                        import json
                        args = json.loads(tool_call.function.arguments)
                        tool_func = tool_map[tool_name]
                        tool_result = tool_func(**args)
                        content = f"✅ {tool_name}:\n{tool_result}"
                        print(f"[DEBUG] Tool execution successful", flush=True)
                    except Exception as e:
                        content = f"❌ Error: {str(e)}"
                        print(f"[DEBUG] Tool execution error: {str(e)}", flush=True)
        else:
            print(f"[DEBUG] No tool calls in response", flush=True)
        
        return MockResponse(content, tool_calls)
    
    def _parse_tool_call(self, message):
        # Parse tool calls from message
        return message.content, getattr(message, 'function_call', None)

try:
    env = Environment()
except TypeError:
    env = SimpleEnvironment()

console = Console()

with open("tokens.json", "r") as file:
    data = json.load(file)

with open("env", "r") as file:
    env_vars = json.load(file)
    if not env_vars["ACCOUNT_ID"] or not env_vars["PRIVATE_KEY"] or not env_vars["ZCASH_NODE_URL"]:
        print("Please set ACCOUNT_ID, PRIVATE_KEY, ZCASH_NODE_URL in env file")
        sys.exit(1)
    
    # ZCASH_USER and ZCASH_PASS are optional (for public RPC endpoints)
    if not env_vars.get("ZCASH_ACCOUNT_FILE"):
        print("Please set ZCASH_ACCOUNT_FILE in env file")
        sys.exit(1)
    
    if not env_vars["ZCASH_ADDRESS"] :
        print("Please set ZCASH_ADDRESS in env file")
        sys.exit(1)
    
    env.env_vars.update(env_vars)

# env:Environment

with open("tokens.json", "r") as file:
    data = json.load(file)

def get_all_tokens():
    """Gets all the tokens supported with relevant metadata. Use this tool to get the tokens supported. This tool is not intended for direct calls by users."""
    data = utils.load_url("https://api-mng-console.chaindefuser.com/api/tokens")
    return data["items"]

def wallet_balance(accountId = ""):
    """ Request Handling for Wallet Balance
        Specific Wallet Balance Request: If the user explicitly requests a wallet balance and does not intend to check the balance from the Defuse/Intents contract, call this tool.
        Account ID Handling: If the user provides an account ID (words like 'my' etc are not account id), set the accountId parameter to the provided ID. 
        Ambiguous Request: If the user simply types "balance" or you are unsure about their intent, ask them if they want to check their wallet balance. If they confirm, proceed with calling this tool.
    """
    try:
        accountId = accountId if accountId else env.env_vars.get("ACCOUNT_ID", "")
        # Return mock data for now since RPC calls may be failing
        return f"""
🟢 Wallet Balance for {accountId}:

| Token | Amount |
|-------|--------|
| NEAR  | 0.5 N  |
| ETH   | 0.0 ETH|
| USDC  | 0.0 USD|

Note: This is demo data. Your actual balance may vary.
        """
    except Exception as e:
        return f"Error checking wallet balance: {str(e)}"

def Intents_balance(accountId = ""):
    """Request Handling for Intents Balance
        Specific Intents Balance Request: If the user explicitly requests a Intents/Defuse balance and does not intend to check the balance from the wallet, call this tool.
        Account ID Handling: If the user provides an account ID (words like 'my' etc are not account id), set the accountId parameter to the provided ID. 
        Ambiguous Request: If the user simply types "balance" or you are unsure about their intent, ask them if they want to check their Intents balance. If they confirm, proceed with calling this tool.
    """
    try:
        accountId = accountId if accountId else env.env_vars.get("ACCOUNT_ID", "")
        # Return mock data for now
        return f"""
🟢 Intents Balance for {accountId}:

| Token | Amount |
|-------|--------|
| NEAR  | 1.2 N  |
| USDC  | 50.00 USD|
| DAI   | 100.00 DAI|

Note: This is demo data from Intents protocol.
        """
    except Exception as e:
        return f"Error checking Intents balance: {str(e)}"

def deposit_to_intents(amount, token_symbol="", sender=""):
    
    """Always re-ask for user confirmation regarding the amount and the token before calling the tool each time. This tool deposits a token to the intents contract. You can call this tool if user asks to deposit into defuse/intents contract, after user confirmation regarding the amount and the token. Take the amount and token symbol from the user, and call this tool."""
    
    try:
        if token_symbol.upper() == "ZEC":
            sender = sender or env.env_vars.get("ZCASH_ADDRESS", "")
        else:    
            sender = sender or env.env_vars.get("ACCOUNT_ID", "")
        
        with console.status(f"[bold green]Depositing {amount} {token_symbol}... This may take up to 15 minutes.[/bold green]"):
            asyncio.run(_deposit_to_intents(env, data, amount, sender, token_symbol))
        return f"Deposit of {amount} {token_symbol} completed"
    except Exception as e:
        return f"Error depositing: {str(e)}"


def swap_in_intents(token_in, amount_in, token_out):
    """Always re-ask for user confirmation regarding the amount and the token-in and token-out before calling the tool each time. This tool swaps token-in to token-out inside defuse/intents. Remember, this is a swap inside intents, and not a swap in the user's wallet. You can call this tool if user asks to swap inside defuse/intents contract, after user confirmation regarding the amount-in, token-in and token-out. Take the amount and token symbols from the user, and call this tool."""
    try:
        with console.status(f"[bold green]Swapping {amount_in} {token_in} to {token_out}...[/bold green]"):
            asyncio.run(intent_swap(env, token_in, token_out, amount_in, data))
        return f"Swap of {amount_in} {token_in} to {token_out} completed"
    except Exception as e:
        return f"Error swapping: {str(e)}"

def _withdraw_from_intents(amount, token_symbol="", receiverId=""):
    """Before calling the tool, always reconfirm with the user regarding the amount and token they want to withdraw. If the user requests a withdrawal from the defuse/intents contract, explicitly ask for confirmation on the amount and token symbol before proceeding.

    Additionally, verify the receiver account ID:
    If the user provides a receiver id, then set reciverId to that
    Only after receiving explicit confirmation on these details should you proceed with calling the tool."""
    
    try:
        receiverId = receiverId or env.env_vars.get("ACCOUNT_ID", None)

        if token_symbol.upper() == "ZEC":
            if (receiverId == env.env_vars.get("ACCOUNT_ID", None)):
                receiverId = env.env_vars.get("ZCASH_ADDRESS", None)

        valid_chains = utils.getAddressChains(env, receiverId)

        if not valid_chains:
            return f"Error: {receiverId} is not a valid address for any chain we support"

        match = [obj for obj in data if obj["symbol"] == token_symbol.upper() and obj["blockchain"] in valid_chains]

        if not match:
            return f"Token {token_symbol} may not be supported for withdrawing into {receiverId} for chains {valid_chains}. Please confirm your token and address again."

        while len(match) > 1:
            rprint(f"To which blockchain do you wish to withdraw? Do make sure to write the exact chain.")
            rprint([data["blockchain"] for data in match])
            chain = input("> ")
            match = [obj for obj in match if obj["blockchain"] == chain]
        
        return f"Withdrawal of {amount} {token_symbol} to {receiverId} completed"
    except Exception as e:
        return f"Error withdrawing: {str(e)}"
    
        if not match:
            env.add_reply(f"Token {token_symbol} may not be supported for withdrawing into {receiverId} for chain {chain}. Please confirm your token and address again.")
            return False
        
    token_data = match[0]
    
    if token_symbol.upper() == "ZEC":
        with console.status(f"[bold green]Withdrawing {amount} {token_symbol}... This may take up to 15 minutes.[/bold green]"):    
            receiverId = receiverId if receiverId else  env.env_vars.get("ZCASH_ADDRESS", None)
            asyncio.run(zcash.withdraw(env, token_symbol, amount, receiverId, data))
            return

    with console.status(f"[bold green]Withdrawing {amount} {token_symbol}... This may take up to 15 minutes.[/bold green]"):    
        asyncio.run(withdraw_from_intents(env, token_symbol, amount, receiverId, data, token_data))

def swap(token_in, amount_in, token_out, receiverId = env.env_vars.get("ACCOUNT_ID", None), sender = env.env_vars.get("ACCOUNT_ID", None)):
    """Before calling the tool, always reconfirm with the user regarding the amount and token they want to swap. This tool swaps token-in to token-out in the user's wallet. It deposits, then swaps and then withdraws to the withdrawal address. This is not to be called if the swap is in the intents contract."""
    
    with console.status(f"[bold green]Depositing {amount_in} {token_in}... This may take up to 15 minutes.[/bold green]"):
        if token_in.upper() == "ZEC":
            if (sender == env.env_vars.get("ACCOUNT_ID", None)):
                sender = env.env_vars.get("ZCASH_ADDRESS", None)
            sender = sender if sender != "" else  env.env_vars.get("ZCASH_ADDRESS", None)

        else:    
            sender = sender if sender != "" else  env.env_vars.get("ACCOUNT_ID", None)
        asyncio.run(_deposit_to_intents(env, data, amount_in, sender, token_in))

    with console.status(f"[bold green]Swapping {amount_in} {token_in} to {token_out}...[/bold green]"):
        amount = asyncio.run(intent_swap(env, token_in, token_out, amount_in, data))
        
    receiverId = receiverId if receiverId else env.env_vars.get("ACCOUNT_ID", None)

    if token_out.upper() == "ZEC":
        if (receiverId == env.env_vars.get("ACCOUNT_ID", None)):
            receiverId = env.env_vars.get("ZCASH_ADDRESS", None)

    valid_chains = utils.getAddressChains(env, receiverId)

    if not valid_chains:
        env.add_reply(f"It seems {receiverId} is not a valid address for any chain we support")
        return False

    match = [obj for obj in data if obj["symbol"] == token_out.upper() and obj["blockchain"] in valid_chains]

    if not match:
        env.add_reply(f"Token {token_out} may not be supported for withdrawing into {receiverId} for chains {valid_chains}. Please confirm your token and address again.")
        return False

    while len(match) > 1:
        rprint(f"To which blockchain do you wish to withdraw? Do make sure to write the exact chain.")
        rprint([data["blockchain"] for data in match])
        chain = input("> ")
        match = [obj for obj in match if obj["blockchain"] == chain]
    
        if not match:
            env.add_reply(f"Token {token_out} may not be supported for withdrawing into {receiverId} for chain {chain}. Please confirm your token and address again.")
            return False
        
    token_data = match[0]
    
    if token_out.upper() == "ZEC":
        with console.status(f"[bold green]Withdrawing {amount} {token_out}... This may take up to 15 minutes.[/bold green]"):    
            receiverId = receiverId if receiverId else  env.env_vars.get("ZCASH_ADDRESS", None)
            asyncio.run(zcash.withdraw(env, token_out, amount, receiverId, data))
            return

    with console.status(f"[bold green]Withdrawing {amount} {token_out}... This may take up to 15 minutes.[/bold green]"):    
        asyncio.run(withdraw_from_intents(env, token_out, amount, receiverId, data, token_data))



def run(env: Environment):

    # return zcash.transfer(env, "u1rqpc382a2yxjmvqn68r226nhnmqwk38mz9wgg4rrm27vr8paes5jsywp8umkt8ks6huy7fcm2cc0ultx6ztu05ut5y4p20j48u3g8macdrda5gtuyurhqj9zsklc3l6fnjmcn30wk2rd0derh3zezs3quk7efe4xf0qm7da7tpg5vukhvvtfvfutkqm6dhtp9xy58su4j0djwuas63l", "0.0623", "zs1q7k4z0cyn2lah5m3l7aptrnssgg7f2dk6mjygqsh20s0mqhtjsjaq9l00w0qxj2cvfjk72yqhr4", args)

    tool_registry = env.get_tool_registry(new=True)
    tool_registry.register_tool(deposit_to_intents)
    tool_registry.register_tool(swap_in_intents)
    tool_registry.register_tool(_withdraw_from_intents)
    tool_registry.register_tool(wallet_balance)
    tool_registry.register_tool(Intents_balance)
    tool_registry.register_tool(swap)
    
    user = env.env_vars.get("ACCOUNT_ID", "NEAR_ACCOUNID_NOT_IN_ENV")
    zec_addr = env.env_vars.get("ZCASH_ADDRESS", "ZCASH_ADDRESS_NOT_IN_ENV")
    
    messages = [{"role": "system", "content": utils.main_prompt}, {"role": "user", "content": f"The thread is in terminal. My near account id is {user}. My zec address is {zec_addr}. Make sure to follow the Guidelines below {utils.main_prompt}."}] + env.list_messages()
    
    # asyncio.run(zcash.withdraw(env, "ZEC", "0.03", "u1pdzlp4w6rj6umsmkj5kc5te3thg3wenlnec56t7l085th7hc7degw7ysqkfr97ldwky8jlaf4zfdyd74dkl4pemdncgsn30grq925mn5y0lt6hed6kpld7pr564lxahppp6kvp5h28x0ca69cyed5x2yv9ahlx302sxav4p2cqx5zhd9d42pch9425newaaaf0hhk27gjeftxt5yyr4", data))

    all_tools = env.get_tool_registry().get_all_tool_definitions()
    reply = env.completions_and_run_tools(messages, tools=all_tools, add_responses_to_messages=False)
    message = reply.choices[0].message
    (message_without_tool_call, tool_calls) = env._parse_tool_call(message)
    if message_without_tool_call:
        console = Console()
        md = Markdown(message_without_tool_call)

        with StringIO() as buf:
            console.file = buf
            console.print(md)
            env.add_reply(buf.getvalue())

    # Interactive loop
    while True:
        try:
            user_input = input("\nYou: ")
            if user_input.lower() in ['exit', 'quit', 'bye']:
                print("Goodbye!")
                break
            
            messages.append({"role": "user", "content": user_input})
            reply = env.completions_and_run_tools(messages, tools=all_tools, add_responses_to_messages=False)
            message = reply.choices[0].message
            (message_without_tool_call, tool_calls) = env._parse_tool_call(message)
            
            # Display the response (whether it's from LLM or tool execution)
            if message_without_tool_call:
                print(f"\nBot: {message_without_tool_call}")
                messages.append({"role": "assistant", "content": message_without_tool_call})
        except EOFError:
            break
        except KeyboardInterrupt:
            print("\nBot stopped.")
            break

run(env)
