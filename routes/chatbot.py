from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required, current_user
from database.database import db
from datetime import datetime

chatbot_bp = Blueprint('chatbot', __name__)

@chatbot_bp.route('/chat')
@login_required
def chat():
    """Render the chatbot interface"""
    return render_template('chatbot.html')

@chatbot_bp.route('/api/chat/send', methods=['POST'])
@login_required
def send_message():
    """Process chatbot messages"""
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({'error': 'Empty message'}), 400
        
        # Import models here to avoid circular imports
        from models.chatbot import ChatSession, ChatMessage
        
        # Get or create chat session for user
        session = ChatSession.query.filter_by(user_id=current_user.id).order_by(ChatSession.updated_at.desc()).first()
        if not session:
            session = ChatSession(user_id=current_user.id)
            db.session.add(session)
            db.session.commit()
        
        # Save user message
        user_msg = ChatMessage(
            session_id=session.id,
            message=user_message,
            is_bot=False
        )
        db.session.add(user_msg)
        
        # Generate bot response
        bot_response = generate_bot_response(user_message, current_user)
        
        # Save bot response
        bot_msg = ChatMessage(
            session_id=session.id,
            message=bot_response,
            is_bot=True
        )
        db.session.add(bot_msg)
        
        # Update session timestamp
        session.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'bot_response': bot_response,
            'session_id': session.id
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to process message'}), 500

def generate_bot_response(user_message, user):
    """Generate appropriate response based on user message and role"""
    message_lower = user_message.lower()
    
    # Results-related queries
    if any(word in message_lower for word in ['result', 'grade', 'score', 'mark']):
        if user.role.value == 'student':
            return "I can help you with your results! Your recent results would be available in the 'Results' section. Would you like me to direct you there?"
        else:
            return "Results management is available in the lecturer or admin portal depending on your role."
    
    # Payment-related queries
    elif any(word in message_lower for word in ['payment', 'fee', 'tuition', 'pay']):
        return "You can check your payment status and make payments in the 'Payments' section. I can show you any outstanding balances or payment history."
    
    # Course-related queries
    elif any(word in message_lower for word in ['course', 'subject', 'register', 'enroll']):
        if user.role.value == 'student':
            return "Course registration typically opens at the beginning of each semester. You can register for courses through the student portal under 'Course Registration'."
        else:
            return "Course management options are available in the lecturer portal where you can view assigned courses and student lists."
    
    # General help
    elif any(word in message_lower for word in ['help', 'support', 'problem', 'issue']):
        return "I'm here to help! You can contact student support at support@cavendish.edu.zm or call +260 123 456 789 for immediate assistance."
    
    # Greetings
    elif any(word in message_lower for word in ['hello', 'hi', 'hey', 'greetings']):
        return f"Hello {user.first_name}! I'm your Cavendish University assistant. How can I help you with your academic journey today?"
    
    # Default response
    else:
        return "I understand you're asking about: '" + user_message + "'. For detailed information about specific academic matters, please visit the relevant section in your portal or contact the administration office for personalized assistance."