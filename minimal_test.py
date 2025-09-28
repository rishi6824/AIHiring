#!/usr/bin/env python3
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_minimal():
    try:
        from models.ai_interviewer import AIInterviewer
        print("✓ AIInterviewer imported")
        
        ai = AIInterviewer()
        questions = ai.get_questions('software_engineer')
        print(f"✓ Got {len(questions)} questions")
        
        # Test answer analysis
        score, feedback, analysis = ai.analyze_answer('software_engineer', 0, "Object-oriented programming has four main principles.")
        print(f"✓ Answer analysis working - Score: {score}")
        
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

if __name__ == "__main__":
    if test_minimal():
        print("Minimal test passed! The core should work.")
    else:
        print("Minimal test failed.")