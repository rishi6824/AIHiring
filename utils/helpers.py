import os
import re

ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def clean_text(text):
    """Clean and normalize text"""
    if not text:
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters but keep basic punctuation
    text = re.sub(r'[^\w\s\.\,\!\?\-]', '', text)
    
    return text.strip()

def calculate_score(answers):
    """Calculate overall interview score"""
    if not answers:
        return 0
    
    total_score = sum(answer.get('score', 0) for answer in answers)
    max_possible = len(answers) * 10
    
    return (total_score / max_possible) * 100 if max_possible > 0 else 0

def get_feedback_level(percentage):
    """Get feedback level based on score percentage"""
    if percentage >= 80:
        return "Excellent"
    elif percentage >= 60:
        return "Good"
    elif percentage >= 40:
        return "Average"
    else:
        return "Needs Improvement"