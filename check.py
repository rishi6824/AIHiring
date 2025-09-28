#!/usr/bin/env python3
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def check_imports():
    try:
        from models.ai_interviewer import AIInterviewer
        print("✓ AIInterviewer imported successfully")
        
        from models.resume_analyzer import ResumeAnalyzer
        print("✓ ResumeAnalyzer imported successfully")
        
        from models.question_generator import QuestionGenerator
        print("✓ QuestionGenerator imported successfully")
        
        from models.speech_processor import SpeechProcessor
        print("✓ SpeechProcessor imported successfully")
        
        return True
    except Exception as e:
        print(f"✗ Import error: {e}")
        return False

def test_components():
    try:
        from models.ai_interviewer import AIInterviewer
        ai = AIInterviewer()
        questions = ai.get_questions('software_engineer')
        print(f"✓ AIInterviewer working - {len(questions)} questions")
        
        from models.question_generator import QuestionGenerator
        qg = QuestionGenerator()
        gen_questions = qg.generate_questions('software_engineer', {})
        print(f"✓ QuestionGenerator working - {len(gen_questions)} questions")
        
        return True
    except Exception as e:
        print(f"✗ Component test error: {e}")
        return False

if __name__ == "__main__":
    print("Checking model imports...")
    if check_imports() and test_components():
        print("All systems go! 🚀")
    else:
        print("Some components need fixing ⚠️")