# 🌑 ShadowSpend

**ShadowSpend** is a privacy-preserving AI agent that allows users to spend ZEC using natural language while keeping all sensitive data — wallet keys, intentions, and transaction logic — fully confidential inside a **Trusted Execution Environment (TEE)**.

By leveraging **NEAR AI** for secure private inference and **NEAR Intents** for cross-chain settlement, ShadowSpend autonomously interprets user requests, selects optimal routes, and executes shielded or transparent ZEC transactions with guaranteed privacy and correctness.

## 🚀 Features

- **Natural Language Interface**: Simply tell ShadowSpend what you want to do
- **Privacy First**: All sensitive data stays encrypted inside the TEE
- **Autonomous Execution**: Intent parsing, decision-making, and transaction signing all in one
- **Cross-Chain Settlement**: Seamless integration with NEAR Intents protocol
- **Shielded Transactions**: Full Zcash privacy support

## 💬 Usage Examples

```
"Send 0.2 ZEC privately."

"Donate 0.1 ZEC to privacy nonprofits."

"Swap 1 ZEC to NEAR and stake it."

"Pay my VPN every month using ZEC."
```

ShadowSpend handles everything: intent parsing, decision-making, route optimization, transaction signing inside the enclave, and final execution through Intents solvers. The result is a powerful, autonomous, and fully private financial agent tailored for ZEC holders.

## 📁 Project Structure

```
ShadowSpend/
├── backend/          # Core agent logic, Zcash integration, NEAR Intents
│   ├── agent.py      # Main AI agent and CLI
│   ├── zcash.py      # Zcash wallet and transaction management
│   ├── utils.py      # Utility functions
│   ├── intents/      # NEAR Intents protocol integration
│   ├── tokens.json   # Supported tokens metadata
│   ├── env           # Environment configuration
│   └── ...
└── frontend/         # Frontend applications (coming soon)
```

## 🛠️ Technologies

- **NEAR AI**: Secure private inference in TEE
- **Zcash**: Privacy-preserving cryptocurrency
- **NEAR Intents**: Cross-chain transaction settlement
- **Python**: Backend implementation
- **OpenAI**: LLM integration for natural language processing

## 📦 Getting Started

### Backend Setup

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export OPENAI_API_KEY="your-key"
python agent.py
```

### Configuration

Create a `env` file in the backend folder:

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

## 🔐 Privacy & Security

- All wallet keys and private data remain encrypted inside the TEE
- Transaction logic and routing decisions are computed privately
- No sensitive data is exposed to external services
- Full Zcash shielding support for transaction privacy

## 📝 License

MIT

---

**ShadowSpend**: Making private payments as easy as natural language. 🌑
