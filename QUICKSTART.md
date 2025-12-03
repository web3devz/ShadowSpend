# 🚀 ShadowSpend - Quick Start Guide

## Setup Instructions

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment

Copy the template and fill in your credentials:

```bash
cp env_example env
```

Edit `env` with your credentials:
```json
{
    "ACCOUNT_ID": "your.near",
    "PRIVATE_KEY": "ed25519:your-private-key",
    "ZCASH_NODE_URL": "https://mainnet.zecnode.io:8232",
    "ZCASH_USER": "",
    "ZCASH_PASS": "",
    "ZCASH_ACCOUNT_FILE": "/tmp/zcash_account.txt",
    "ZCASH_ADDRESS": "t1your-zcash-address"
}
```

### 3. Set OpenAI API Key

```bash
export OPENAI_API_KEY="sk-proj-your-key"
```

### 4. Run the Server

**Option A: Web UI + Backend**
```bash
cd ..
python server.py
```
Then open `http://localhost:5000` in your browser.

**Option B: CLI Only**
```bash
cd backend
python agent.py
```

## Features

### Natural Language Commands

Simply type commands in the chat:

- 💸 **Send**: "Send 0.2 ZEC privately to t1address..."
- 🔄 **Swap**: "Swap 1 ZEC to NEAR"
- 🤝 **Donate**: "Donate 0.1 ZEC to privacy nonprofits"
- 📊 **Balance**: "Check my wallet balance"
- ⚡ **Stake**: "Stake 10 NEAR tokens"
- 💳 **Pay**: "Pay my VPN subscription with ZEC"

### Core Capabilities

✅ Privacy-preserving Zcash transactions
✅ Natural language intent parsing
✅ Cross-chain settlement via NEAR Intents
✅ Autonomous execution
✅ Shielded transaction support

## Architecture

```
Frontend (index.html)
    ↓
Web Server (server.py) 
    ↓
AI Agent (backend/agent.py)
    ├── OpenAI API (GPT-4o-mini)
    ├── Zcash Integration (zcash.py)
    └── NEAR Intents (intents/)
```

## API Endpoints

### Chat
- `POST /api/chat` - Send a message
- `GET /api/chat/history` - Get chat history
- `POST /api/chat/clear` - Clear chat

### Status
- `GET /api/status` - Server status

## Troubleshooting

### Port already in use
```bash
python server.py  # Will auto-find next available port
```

### Agent not loading
The web UI will work in demo mode if the agent fails to load.
Check `backend/env` file configuration.

### OPENAI_API_KEY not set
```bash
export OPENAI_API_KEY="your-key"
python server.py
```

## Development

### Backend Development
- Edit `backend/agent.py` for agent logic
- Edit `backend/zcash.py` for Zcash integration
- Edit `backend/utils.py` for NEAR utilities

### Frontend Development
- Edit `frontend/index.html` for UI
- API calls in JavaScript connect to `server.py`

## Production Deployment

1. Update `server.py` to use production WSGI server (Gunicorn)
2. Set `debug=False`
3. Use environment variables for secrets
4. Deploy with Docker or your preferred platform

Example Dockerfile:
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "server:app"]
```

## Support

For issues or questions, refer to:
- `README.md` - Project overview
- `backend/README.md` - Backend documentation
- `frontend/README.md` - Frontend roadmap
