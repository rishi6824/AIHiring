from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import os
import json
from datetime import datetime
from config import Config
from models.ai_interviewer import AIInterviewer
from models.resume_analyzer import ResumeAnalyzer
from models.speech_processor import SpeechProcessor
from models.question_generator import QuestionGenerator
from utils.helpers import allowed_file, calculate_score, clean_text
import secrets
import ssl

app = Flask(__name__)
app.config.from_object(Config)

# Create upload directory
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize AI components
ai_interviewer = AIInterviewer()
resume_analyzer = ResumeAnalyzer()
speech_processor = SpeechProcessor()
question_generator = QuestionGenerator()

# Add CORS headers for microphone access
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/debug/models')
def debug_models():
    """Test if all models are working"""
    results = {}
    
    try:
        # Test AI Interviewer
        questions = ai_interviewer.get_questions('software_engineer')
        results['ai_interviewer'] = f"Working - {len(questions)} questions"
    except Exception as e:
        results['ai_interviewer'] = f"Error: {e}"
    
    try:
        # Test Question Generator
        questions = question_generator.generate_questions('software_engineer', {})
        results['question_generator'] = f"Working - {len(questions)} questions"
    except Exception as e:
        results['question_generator'] = f"Error: {e}"
    
    try:
        # Test Resume Analyzer
        analysis = resume_analyzer.analyze_resume_text("Sample resume text with Python and Java skills")
        results['resume_analyzer'] = f"Working - Skills: {len(analysis['skills'])}"
    except Exception as e:
        results['resume_analyzer'] = f"Error: {e}"
    
    try:
        # Test Speech Processor
        speech_processor.speech_to_text(None)
        results['speech_processor'] = "Working"
    except Exception as e:
        results['speech_processor'] = f"Error: {e}"
    
    return jsonify(results)

@app.route('/debug/start_interview_direct')
def debug_start_interview_direct():
    """Direct test of interview start"""
    session.clear()
    
    # Use AI Interviewer directly (bypass question generator)
    questions = ai_interviewer.get_questions('software_engineer')
    
    # Initialize interview session
    session['interview_id'] = secrets.token_hex(16)
    session['current_question'] = 0
    session['score'] = 0
    session['responses'] = []
    session['questions'] = questions
    session['job_role'] = 'software_engineer'
    session['start_time'] = datetime.now().isoformat()
    session['enable_voice'] = False
    
    return redirect(url_for('interview_room'))


@app.route('/debug_interview_state')
def debug_interview_state():
    """Debug current interview state"""
    if 'interview_id' not in session:
        return jsonify({'error': 'No active interview'})
    
    return jsonify({
        'current_question': session['current_question'],
        'total_questions': len(session['questions']),
        'questions': session['questions'],
        'completed': session['current_question'] >= len(session['questions'])
    })


@app.route('/check_permissions')
def check_permissions():
    """Check if browser supports media devices"""
    return jsonify({
        'https': request.is_secure,
        'host': request.host,
        'scheme': request.scheme
    })

@app.route('/auto_next_question')
def auto_next_question():
    """Automatically redirect to next question or results"""
    if 'interview_id' not in session:
        return redirect(url_for('index'))
    
    current_q = session['current_question']
    questions = session['questions']
    
    if current_q >= len(questions):
        return redirect(url_for('results'))
    else:
        return redirect(url_for('interview_room'))

@app.route('/analyze_resume', methods=['GET', 'POST'])
def analyze_resume():
    if request.method == 'POST':
        if 'resume' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['resume']
        if file and allowed_file(file.filename):
            try:
                # Save file
                filename = secrets.token_hex(8) + '_' + file.filename
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                
                # Analyze resume
                analysis = resume_analyzer.analyze_resume_file(filepath)
                
                # Store analysis in session
                session['resume_analysis'] = analysis
                session['resume_file'] = filename
                
                return render_template('resume_analysis.html', analysis=analysis)
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        return jsonify({'error': 'Invalid file type'}), 400
    
    return render_template('resume_analysis.html')

@app.route('/chatbot')
def chatbot_page():
    return render_template('chatbot.html')

@app.route('/test_camera')
def test_camera():
    return render_template('test_camera.html')

@app.route('/test_questions')
def test_questions():
    """Test question flow"""
    session.clear()
    questions = [
        {'question': 'Question 1: Tell me about yourself', 'type': 'behavioral'},
        {'question': 'Question 2: What are your strengths?', 'type': 'behavioral'},
        {'question': 'Question 3: Where do you see yourself in 5 years?', 'type': 'behavioral'}
    ]
    
    session['interview_id'] = 'test'
    session['current_question'] = 0
    session['questions'] = questions
    session['responses'] = []
    
    return redirect('/interview_room')

@app.route('/start_video_interview', methods=['POST'])
def start_video_interview():
    session.clear()
    
    # Get job role and use resume analysis if available
    job_role = request.form.get('job_role', 'software_engineer')
    resume_analysis = session.get('resume_analysis', {})
    
    # Generate personalized questions based on resume
    questions = question_generator.generate_questions(job_role, resume_analysis)
    
    # Initialize interview session
    session['interview_id'] = secrets.token_hex(16)
    session['current_question'] = 0
    session['score'] = 0
    session['responses'] = []
    session['questions'] = questions
    session['job_role'] = job_role
    session['start_time'] = datetime.now().isoformat()
    session['enable_voice'] = True
    
    return redirect(url_for('video_interview'))

@app.route('/video_interview')
def video_interview():
    if 'interview_id' not in session:
        return redirect(url_for('index'))
    
    return render_template('video_interview.html',
                         enable_voice=session.get('enable_voice', True))

@app.route('/interview_room')
def interview_room():
    if 'interview_id' not in session:
        return redirect(url_for('index'))
    
    current_q = session['current_question']
    questions = session['questions']
    
    # Check if interview is completed
    if current_q >= len(questions):
        return redirect(url_for('results'))
    
    question = questions[current_q]
    return render_template('interview_room.html',
                         question=question,
                         question_num=current_q + 1,
                         total_questions=len(questions),
                         enable_voice=session.get('enable_voice', True))
    
    
@app.route('/submit_answer', methods=['POST'])
def submit_answer():
    if 'interview_id' not in session:
        return jsonify({'error': 'No active interview'}), 400
    
    current_q = session['current_question']
    questions = session['questions']
    
    # Check if we've exceeded the question count
    if current_q >= len(questions):
        return jsonify({
            'completed': True,
            'next_question': current_q,
            'score': 0,
            'feedback': 'Interview completed!',
            'detailed_analysis': {}
        })
    
    answer = request.form.get('answer', '')
    job_role = session['job_role']
    resume_analysis = session.get('resume_analysis', {})
    
    # Analyze the answer
    score, feedback, detailed_analysis = ai_interviewer.analyze_answer(
        job_role, current_q, answer, resume_analysis
    )
    
    # Add AI personality to feedback
    if score >= 8:
        ai_feedback = f"Excellent! {feedback} That was a well-structured response."
    elif score >= 6:
        ai_feedback = f"Good job. {feedback} You're on the right track."
    elif score >= 4:
        ai_feedback = f"Okay. {feedback} Let's work on improving this."
    else:
        ai_feedback = f"I see. {feedback} We'll practice more on this area."
    
    # Store response
    session['responses'].append({
        'question_index': current_q,
        'question': questions[current_q]['question'],
        'answer': answer,
        'score': score,
        'feedback': ai_feedback,
        'detailed_analysis': detailed_analysis
    })
    
    session['score'] += score
    session['current_question'] += 1
    
    # Check if interview is completed
    completed = session['current_question'] >= len(questions)
    
    return jsonify({
        'next_question': session['current_question'],
        'score': score,
        'feedback': ai_feedback,
        'detailed_analysis': detailed_analysis,
        'completed': completed
    })

@app.route('/process_voice', methods=['POST'])
def process_voice():
    if 'interview_id' not in session:
        return jsonify({'error': 'No active interview'}), 400
    
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file'}), 400
    
    audio_file = request.files['audio']
    
    try:
        # Convert speech to text
        text = speech_processor.speech_to_text(audio_file)
        
        if text:
            return jsonify({
                'success': True,
                'text': text
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Could not understand audio'
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/results')
def results():
    if 'interview_id' not in session:
        return redirect(url_for('index'))
    
    total_score = session['score']
    max_possible = len(session['responses']) * 10
    percentage = (total_score / max_possible * 100) if max_possible > 0 else 0
    
    # Generate overall feedback
    overall_feedback = ai_interviewer.generate_overall_feedback(
        session['responses'], session.get('resume_analysis', {})
    )
    
    return render_template('results.html',
                         score=total_score,
                         percentage=percentage,
                         responses=session['responses'],
                         overall_feedback=overall_feedback,
                         resume_analysis=session.get('resume_analysis'))

@app.route('/get_next_question')
def get_next_question():
    if 'interview_id' not in session:
        return jsonify({'error': 'No active interview'}), 400
    
    current_q = session['current_question']
    questions = session['questions']
    
    if current_q >= len(questions):
        return jsonify({'completed': True})
    
    question = questions[current_q]
    return jsonify({
        'question': question['question'],
        'question_num': current_q + 1,
        'total_questions': len(questions),
        'type': question.get('type', 'technical')
    })

def create_ssl_context():
    """Create SSL context with fallback"""
    try:
        # Method 1: Use existing certificate files
        if os.path.exists('cert.pem') and os.path.exists('key.pem'):
            context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
            context.load_cert_chain('cert.pem', 'key.pem')
            return context
        else:
            # Method 2: Create self-signed certificate programmatically
            from OpenSSL import crypto
            import tempfile
            
            # Create a key pair
            k = crypto.PKey()
            k.generate_key(crypto.TYPE_RSA, 4096)
            
            # Create a self-signed cert
            cert = crypto.X509()
            cert.get_subject().C = "US"
            cert.get_subject().ST = "State"
            cert.get_subject().L = "City"
            cert.get_subject().O = "Organization"
            cert.get_subject().OU = "Organization Unit"
            cert.get_subject().CN = "localhost"
            cert.set_serial_number(1000)
            cert.gmtime_adj_notBefore(0)
            cert.gmtime_adj_notAfter(365*24*60*60)
            cert.set_issuer(cert.get_subject())
            cert.set_pubkey(k)
            cert.sign(k, 'sha512')
            
            # Save certificate and key to temporary files
            with open('cert.pem', 'wt') as f:
                f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert).decode('utf-8'))
            with open('key.pem', 'wt') as f:
                f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, k).decode('utf-8'))
            
            context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
            context.load_cert_chain('cert.pem', 'key.pem')
            return context
            
    except Exception as e:
        print(f"SSL context creation failed: {e}")
        return None

if __name__ == '__main__':
    # Try to run with HTTPS first
    ssl_context = create_ssl_context()
    
    if ssl_context:
        print("🚀 Running with HTTPS on https://localhost:5000")
        print("📹 Camera and microphone should work now!")
        print("🔐 Make sure to access via: https://localhost:5000")
        app.run(debug=True, ssl_context=ssl_context, host='0.0.0.0', port=5000)
    else:
        print("⚠️  Running without HTTPS - camera/microphone won't work")
        print("💡 To fix this, run: openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365 -subj '/C=US/ST=State/L=City/O=Organization/CN=localhost'")
        app.run(debug=True, host='0.0.0.0', port=5000)