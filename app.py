# app.py - Main Flask application
from flask import Flask, render_template, request, jsonify, session
import os
import secrets
from datetime import datetime

# Import the MedicalChatbot class
from medical_chatbot import MedicalChatbot

app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = secrets.token_hex(16)

# In-memory storage for chatbot instances
chatbot_instances = {}

@app.route('/')
def index():
    """Render the main application page"""
    # Generate a session ID if not already set
    if 'session_id' not in session:
        session['session_id'] = secrets.token_hex(8)
        chatbot_instances[session['session_id']] = MedicalChatbot()
    
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """Process chat messages from the user"""
    data = request.json
    message = data.get('message', '')
    session_id = session.get('session_id')
    
    if not session_id or session_id not in chatbot_instances:
        return jsonify({'error': 'Invalid session'}), 400
    
    # Use the MedicalChatbot instance to process the message
    chatbot = chatbot_instances[session_id]
    response = chatbot.process_message(message)
    
    return jsonify({
        'message': response,
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

@app.route('/api/history', methods=['GET'])
def get_history():
    """Get the chat history for the current session"""
    session_id = session.get('session_id')
    
    if not session_id or session_id not in chatbot_instances:
        return jsonify({'error': 'Invalid session'}), 400
    
    chatbot = chatbot_instances[session_id]
    
    return jsonify({
        'history': chatbot.conversation_history
    })

@app.route('/check_files')
def check_files():
    """Debug route to check if files exist"""
    css_exists = os.path.exists('static/css/styles.css')
    js_exists = os.path.exists('static/js/app.js')
    index_exists = os.path.exists('templates/index.html')
    
    return jsonify({
        'css_exists': css_exists,
        'js_exists': js_exists,
        'index_exists': index_exists
    })

if __name__ == '__main__':
    app.run(debug=True)