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

app = Flask(__name__)
app.config.from_object(Config)

# Create upload directory
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize AI components
ai_interviewer = AIInterviewer()
resume_analyzer = ResumeAnalyzer()
speech_processor = SpeechProcessor()
question_generator = QuestionGenerator()

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
    session['enable_voice'] = True  # Enable voice input
    
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
    
    answer = request.form.get('answer', '')
    current_q = session['current_question']
    job_role = session['job_role']
    resume_analysis = session.get('resume_analysis', {})
    
    # Analyze the answer
    score, feedback, detailed_analysis = ai_interviewer.analyze_answer(
        job_role, current_q, answer, resume_analysis
    )
    
    # Store response
    session['responses'].append({
        'question_index': current_q,
        'question': session['questions'][current_q]['question'],
        'answer': answer,
        'score': score,
        'feedback': feedback,
        'detailed_analysis': detailed_analysis
    })
    
    session['score'] += score
    session['current_question'] += 1
    
    return jsonify({
        'next_question': session['current_question'],
        'score': score,
        'feedback': feedback,
        'detailed_analysis': detailed_analysis,
        'completed': session['current_question'] >= len(session['questions'])
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

if __name__ == '__main__':
    app.run(debug=True)