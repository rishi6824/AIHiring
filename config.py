import os

class Config:
    SECRET_KEY = 'your-secret-key-here-change-this-in-production'
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # Interview settings
    MAX_QUESTIONS = 10
    QUESTION_TIME_LIMIT = 180  # 3 minutes per question
    
    # Chatbot settings
    CHATBOT_NAME = "InterviewBot"
    MAX_CHAT_HISTORY = 20