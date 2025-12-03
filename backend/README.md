# ShadowSpend Backend

Core AI agent logic for privacy-preserving Zcash transactions.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Running the Agent

```bash
export OPENAI_API_KEY="your-key"
python agent.py
```

## Configuration

Copy `env_example` to `env` and fill in your credentials:

```json
{
    "ACCOUNT_ID": "your.near",
    "PRIVATE_KEY": "ed25519:...",
    "ZCASH_NODE_URL": "https://mainnet.zecnode.io:8232",
    "ZCASH_USER": "",
    "ZCASH_PASS": "",
    "ZCASH_ACCOUNT_FILE": "/tmp/zcash_account.txt",
    "ZCASH_ADDRESS": "t1..."
}
```

## Key Components

- **agent.py**: Main AI agent with OpenAI integration
- **zcash.py**: Zcash wallet management and transactions
- **utils.py**: NEAR integration and utility functions
- **intents/**: NEAR Intents protocol module
- **serializer.py**: Borsh serialization helpers
