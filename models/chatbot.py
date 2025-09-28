import random
import re

class InterviewChatbot:
    def __init__(self):
        self.responses = self._load_responses()
    
    def _load_responses(self):
        return {
            'greeting': [
                "Hello! I'm here to help you with your interview preparation. How can I assist you?",
                "Hi there! Ready to practice for your interview? What would you like to know?",
                "Welcome! I'm your interview coach. What questions do you have about the interview process?"
            ],
            'interview_tips': [
                "Research the company thoroughly before the interview and understand their values and mission.",
                "Practice common interview questions but also prepare stories that demonstrate your skills.",
                "Remember to ask thoughtful questions at the end of the interview - it shows genuine interest.",
                "Dress professionally and arrive early (or join the virtual meeting a few minutes early).",
                "Use the STAR method (Situation, Task, Action, Result) for behavioral questions."
            ],
            'technical_interview': [
                "For technical interviews, practice coding problems on platforms like LeetCode or HackerRank.",
                "Explain your thought process out loud during technical interviews - interviewers want to see how you think.",
                "Don't just focus on getting the right answer; focus on writing clean, efficient code.",
                "Review fundamental data structures and algorithms before technical interviews.",
                "Prepare to discuss your technical projects in detail, including challenges you faced."
            ],
            'salary_negotiation': [
                "Research market rates for the position and location before discussing salary.",
                "Let the employer mention numbers first if possible, but be prepared with your range.",
                "Consider the total compensation package, not just base salary.",
                "Be confident but reasonable in your negotiations, and be ready to justify your requested salary.",
                "Practice your negotiation conversation beforehand to feel more comfortable."
            ],
            'behavioral_questions': [
                "Prepare 3-5 stories from your experience that demonstrate key competencies.",
                "Use the STAR method: Situation, Task, Action, Result to structure your answers.",
                "Be specific about your role and contributions in each situation.",
                "Focus on positive outcomes and what you learned from each experience.",
                "Tailor your stories to match the job requirements and company values."
            ],
            'fallback': [
                "I'm not sure I understand. Could you rephrase that?",
                "That's an interesting question. Could you provide more context?",
                "I'm here to help with interview preparation. Could you ask about interview tips, technical questions, or behavioral interviews?",
                "Let me think about that. In the meantime, would you like tips on interview preparation?"
            ]
        }
    
    def get_response(self, user_input):
        user_input = user_input.lower().strip()
        
        # Pattern matching for different types of questions
        if any(word in user_input for word in ['hello', 'hi', 'hey', 'greetings']):
            return random.choice(self.responses['greeting'])
        
        elif any(word in user_input for word in ['tip', 'advice', 'suggest', 'how to']):
            return random.choice(self.responses['interview_tips'])
        
        elif any(word in user_input for word in ['technical', 'code', 'programming', 'algorithm']):
            return random.choice(self.responses['technical_interview'])
        
        elif any(word in user_input for word in ['salary', 'pay', 'compensation', 'money']):
            return random.choice(self.responses['salary_negotiation'])
        
        elif any(word in user_input for word in ['behavioral', 'experience', 'story', 'situation']):
            return random.choice(self.responses['behavioral_questions'])
        
        else:
            return random.choice(self.responses['fallback'])