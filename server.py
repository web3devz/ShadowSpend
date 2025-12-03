"""
ShadowSpend Web Server
Serves the frontend UI and connects to the AI agent backend
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import json
import os
import sys
from pathlib import Path

app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)

# Try to import the agent
try:
    sys.path.insert(0, str(Path(__file__).parent / 'backend'))
    from agent import env, console
except Exception as e:
    print(f"Warning: Could not load agent: {e}")
    env = None

class ChatSession:
    """Manage chat session and messages"""
    def __init__(self):
        self.messages = [
            {
                "role": "assistant",
                "content": "👋 Hello! I'm ShadowSpend, your privacy-first Zcash assistant. What would you like to do today?\n\nExamples:\n- Send 0.2 ZEC privately\n- Swap 1 ZEC to NEAR\n- Donate 0.1 ZEC to privacy nonprofits\n- Check my wallet balance"
            }
        ]

chat_session = ChatSession()

@app.route('/')
def index():
    """Serve the landing page"""
    return app.send_static_file('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages"""
    try:
        data = request.json
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({'error': 'Empty message'}), 400
        
        # Add user message to history
        chat_session.messages.append({
            "role": "user",
            "content": user_message
        })
        
        # Get bot response
        bot_response = get_bot_response(user_message)
        
        # Add bot response to history
        chat_session.messages.append({
            "role": "assistant",
            "content": bot_response
        })
        
        return jsonify({
            'success': True,
            'response': bot_response,
            'messages': chat_session.messages
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/chat/history', methods=['GET'])
def get_history():
    """Get chat history"""
    return jsonify({'messages': chat_session.messages})

@app.route('/api/chat/clear', methods=['POST'])
def clear_chat():
    """Clear chat history"""
    chat_session.messages = [chat_session.messages[0]]  # Keep initial message
    return jsonify({'success': True})

@app.route('/api/status', methods=['GET'])
def status():
    """Get API status"""
    return jsonify({
        'status': 'running',
        'service': 'ShadowSpend Web Server',
        'version': '1.0.0',
        'agent_ready': env is not None
    })

def get_bot_response(user_message: str) -> str:
    """
    Generate bot response based on user message
    In production, this would call the actual agent
    """
    lower = user_message.lower()
    
    responses = {
        'send': '💸 I\'ll help you send ZEC privately. How much would you like to send? (e.g., "0.2 ZEC to t1address...")',
        'swap': '🔄 Great! I can swap ZEC to NEAR or other tokens. What amount and target would you like?',
        'donate': '🤝 That\'s generous! I\'ll process your donation through Intents. Which organization or address?',
        'balance': '📊 Checking your wallet balance... Your wallet contains: NEAR: 0.5, ZEC: 1.2 ZEC (demo data)',
        'stake': '⚡ I can help you stake your tokens. How much NEAR would you like to stake?',
        'pay': '💳 I can set up recurring payments. Which service or address would you like to pay?',
        'privately': '🔐 Absolutely. All transactions will use Zcash shielding for maximum privacy.',
        'crypto': '🪙 I support ZEC, NEAR, and other tokens through the Intents protocol.',
        'help': '''📖 Here's what I can help you with:
- **Send**: "Send 0.2 ZEC privately"
- **Swap**: "Swap 1 ZEC to NEAR"  
- **Donate**: "Donate 0.1 ZEC to privacy nonprofits"
- **Balance**: "Check my wallet"
- **Stake**: "Stake my NEAR tokens"
- **Pay**: "Pay my VPN subscription"

All transactions are fully private and secure!''',
    }
    
    for keyword, response in responses.items():
        if keyword in lower:
            return response
    
    return '✨ I understand. Let me process your request securely in the Trusted Execution Environment. For now, this is a demo response. ' + user_message[:50] + '...'

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"""
    🌑 ShadowSpend Web Server
    
    Frontend: http://localhost:{port}
    API: http://localhost:{port}/api
    
    Status: {'✓ Ready' if env else '⚠ Agent not loaded (demo mode)'}
    """)
    app.run(debug=True, port=port, host='0.0.0.0')
