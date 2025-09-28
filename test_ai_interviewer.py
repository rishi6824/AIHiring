#!/usr/bin/env python3
import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.ai_interviewer import AIInterviewer

def test_ai_interviewer():
    try:
        # Test if we can create an instance
        interviewer = AIInterviewer()
        print("✓ AIInterviewer class imported successfully!")
        
        # Test if we can get questions
        questions = interviewer.get_questions('software_engineer')
        print(f"✓ Retrieved {len(questions)} questions for software_engineer")
        
        # Test answer analysis
        score, feedback, analysis = interviewer.analyze_answer(
            'software_engineer', 
            0, 
            "Object-oriented programming has four main principles: encapsulation, inheritance, polymorphism, and abstraction."
        )
        print(f"✓ Answer analysis completed. Score: {score}/10")
        print(f"✓ Feedback: {feedback}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

if __name__ == "__main__":
    test_ai_interviewer()