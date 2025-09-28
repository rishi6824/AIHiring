import json
import os
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

class AIInterviewer:
    def __init__(self):
        self.questions_file = 'data/questions/interview_questions.json'
        self.questions = self._load_questions()
    
    def _load_questions(self):
        try:
            with open(self.questions_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Warning: Questions file {self.questions_file} not found. Using default questions.")
            return self._get_default_questions()
    
    def _get_default_questions(self):
        return {
            "software_engineer": [
                {
                    "question": "Can you explain object-oriented programming and its main principles?",
                    "type": "technical",
                    "keywords": ["encapsulation", "inheritance", "polymorphism", "abstraction", "classes", "objects"]
                },
                {
                    "question": "Describe a challenging technical problem you solved and how you approached it.",
                    "type": "behavioral",
                    "keywords": ["problem", "solution", "approach", "challenge", "result", "learning"]
                },
                {
                    "question": "How do you ensure code quality and what testing methodologies do you use?",
                    "type": "technical",
                    "keywords": ["testing", "quality", "unit tests", "integration", "code review", "best practices"]
                }
            ],
            "data_scientist": [
                {
                    "question": "Explain the difference between supervised and unsupervised learning.",
                    "type": "technical",
                    "keywords": ["supervised", "unsupervised", "labeled data", "clustering", "classification", "training"]
                },
                {
                    "question": "How do you handle missing data in a dataset?",
                    "type": "technical",
                    "keywords": ["missing data", "imputation", "removal", "analysis", "strategy", "impact"]
                }
            ]
        }
    
    def get_questions(self, job_role):
        return self.questions.get(job_role, self.questions['software_engineer'])
    
    def analyze_answer(self, job_role, question_index, answer, resume_analysis=None):
        questions = self.get_questions(job_role)
        
        if question_index >= len(questions):
            return 0, "Invalid question index", {}
        
        question = questions[question_index]
        
        # Basic analysis
        score = self._calculate_score(answer, question.get('keywords', []))
        feedback = self._generate_feedback(answer, question.get('keywords', []), score)
        analysis = {
            'word_count': len(word_tokenize(answer)),
            'sentences': len(sent_tokenize(answer))
        }
        
        return score, feedback, analysis
    
    def _calculate_score(self, answer, expected_keywords):
        if not answer.strip():
            return 0
        
        answer_lower = answer.lower()
        keywords_found = 0
        
        for keyword in expected_keywords:
            if keyword.lower() in answer_lower:
                keywords_found += 1
        
        # Calculate score based on keyword matches and answer length
        keyword_score = (keywords_found / len(expected_keywords)) * 6 if expected_keywords else 0
        
        # Length score (encourage detailed answers)
        word_count = len(word_tokenize(answer))
        length_score = min(4, word_count / 25)  # Max 4 points for length
        
        total_score = min(10, keyword_score + length_score)
        return round(total_score, 1)
    
    def _generate_feedback(self, answer, expected_keywords, score):
        if score >= 8:
            return "Excellent answer! You covered the key points clearly and thoroughly."
        elif score >= 6:
            return "Good answer. You mentioned some relevant points but could add more detail."
        elif score >= 4:
            return "Average answer. Consider providing more specific examples and details."
        else:
            missing_keywords = [kw for kw in expected_keywords if kw.lower() not in answer.lower()]
            if missing_keywords:
                return f"Try to include concepts like: {', '.join(missing_keywords[:3])}"
            else:
                return "Please provide a more detailed and structured answer."
    
    def generate_overall_feedback(self, responses, resume_analysis):
        if not responses:
            return "No responses to evaluate."
        
        total_score = sum(response['score'] for response in responses)
        average_score = total_score / len(responses)
        
        if average_score >= 8:
            strength = "strong"
        elif average_score >= 6:
            strength = "good"
        elif average_score >= 4:
            strength = "average"
        else:
            strength = "needs improvement"
        
        return f"Overall, you demonstrated {strength} performance in this interview with an average score of {average_score:.1f}/10."