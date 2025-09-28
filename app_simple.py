from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import os
import secrets

app = Flask(__name__)
app.secret_key = 'dev-key-change-in-production'
app.config['UPLOAD_FOLDER'] = 'uploads/resumes'

# Simple AI Interviewer (minimal version)
class SimpleAIInterviewer:
    def __init__(self):
        self.questions = {
            "software_engineer": [
                {"question": "Can you explain object-oriented programming?", "type": "technical"},
                {"question": "Describe a challenging technical problem you solved?", "type": "behavioral"},
                {"question": "How do you ensure code quality?", "type": "technical"}
            ]
        }
    
    def get_questions(self, job_role):
        return self.questions.get(job_role, self.questions["software_engineer"])
    
    def analyze_answer(self, job_role, question_index, answer):
        # Simple scoring based on answer length
        word_count = len(answer.split())
        score = min(10, word_count / 10)
        
        if score >= 8:
            feedback = "Excellent detailed answer!"
        elif score >= 5:
            feedback = "Good answer, could use more details."
        else:
            feedback = "Please provide a more detailed answer."
        
        return round(score, 1), feedback, {"word_count": word_count}

# Initialize AI
ai_interviewer = SimpleAIInterviewer()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start_interview', methods=['POST'])
def start_interview():
    session.clear()
    session['current_question'] = 0
    session['score'] = 0
    session['responses'] = []
    session['job_role'] = request.form.get('job_role', 'software_engineer')
    session['questions'] = ai_interviewer.get_questions(session['job_role'])
    return redirect(url_for('interview'))

@app.route('/interview')
def interview():
    if 'job_role' not in session:
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
                         enable_voice=False)

@app.route('/submit_answer', methods=['POST'])
def submit_answer():
    answer = request.form.get('answer', '')
    current_q = session['current_question']
    job_role = session['job_role']
    
    score, feedback, analysis = ai_interviewer.analyze_answer(job_role, current_q, answer)
    
    session['responses'].append({
        'question_index': current_q,
        'answer': answer,
        'score': score,
        'feedback': feedback
    })
    session['score'] += score
    session['current_question'] += 1
    
    return jsonify({
        'next_question': session['current_question'],
        'score': score,
        'feedback': feedback,
        'completed': session['current_question'] >= len(session['questions'])
    })

@app.route('/results')
def results():
    if 'responses' not in session:
        return redirect(url_for('index'))
    
    total_score = session['score']
    max_possible = len(session['responses']) * 10
    percentage = (total_score / max_possible * 100) if max_possible > 0 else 0
    
    return render_template('results.html',
                         score=total_score,
                         percentage=percentage,
                         responses=session['responses'])

if __name__ == '__main__':
    if not os.path.exists('uploads/resumes'):
        os.makedirs('uploads/resumes')
    app.run(debug=True, port=5001)