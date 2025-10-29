from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user

chatbot_bp = Blueprint('chatbot', __name__)

@chatbot_bp.route('/chat')
@login_required
def chat_interface():
    return render_template('chatbot/chat.html')

@chatbot_bp.route('/send_message', methods=['POST'])
@login_required
def send_message():
    user_message = request.json.get('message', '')
    
    # Simple echo bot for now
    response = f"Hello {current_user.first_name}! You said: '{user_message}'. This is a basic chatbot response."
    
    return jsonify({
        'response': response,
        'user_message': user_message
    })