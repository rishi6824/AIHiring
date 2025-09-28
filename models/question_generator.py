import random

class QuestionGenerator:
    def __init__(self):
        self.base_questions = {
            "software_engineer": [
                {
                    "question": "Can you explain your experience with object-oriented programming?",
                    "type": "technical",
                    "difficulty": "medium"
                },
                {
                    "question": "Describe a time you had to debug a complex issue. What was your approach?",
                    "type": "behavioral", 
                    "difficulty": "medium"
                },
                {
                    "question": "How do you handle code reviews and feedback from teammates?",
                    "type": "behavioral",
                    "difficulty": "easy"
                }
            ],
            "data_scientist": [
                {
                    "question": "Explain the difference between machine learning and deep learning.",
                    "type": "technical",
                    "difficulty": "medium"
                },
                {
                    "question": "How do you validate your machine learning models?",
                    "type": "technical",
                    "difficulty": "hard"
                }
            ]
        }
    
    def generate_questions(self, job_role, resume_analysis, num_questions=3):
        base_questions = self.base_questions.get(job_role, self.base_questions["software_engineer"])
        
        # Return first few questions
        return base_questions[:num_questions]