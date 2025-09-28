import PyPDF2
from docx import Document
import re
import os

class ResumeAnalyzer:
    def __init__(self):
        self.skill_categories = {
            'programming': ['python', 'java', 'javascript', 'c++', 'c#', 'ruby', 'php', 'swift', 'kotlin'],
            'web_tech': ['html', 'css', 'react', 'angular', 'vue', 'django', 'flask', 'node.js', 'express'],
            'databases': ['mysql', 'postgresql', 'mongodb', 'redis', 'sqlite', 'oracle'],
            'cloud': ['aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform', 'jenkins'],
            'data_science': ['pandas', 'numpy', 'tensorflow', 'pytorch', 'scikit-learn', 'r', 'matplotlib'],
            'soft_skills': ['communication', 'leadership', 'teamwork', 'problem-solving', 'creativity', 'adaptability']
        }
    
    def parse_resume(self, file_path):
        filename = file_path.lower()
        
        if filename.endswith('.pdf'):
            return self._parse_pdf(file_path)
        elif filename.endswith('.docx'):
            return self._parse_docx(file_path)
        elif filename.endswith('.txt'):
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            raise ValueError("Unsupported file format")
    
    def _parse_pdf(self, file_path):
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text()
                return text
        except Exception as e:
            return f"Error reading PDF: {str(e)}"
    
    def _parse_docx(self, file_path):
        try:
            doc = Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            return f"Error reading DOCX: {str(e)}"
    
    def analyze_resume_file(self, file_path):
        text = self.parse_resume(file_path)
        return self.analyze_resume_text(text)
    
    def analyze_resume_text(self, text):
        analysis = {}
        
        # Basic text analysis
        words = text.split()
        analysis['word_count'] = len(words)
        analysis['char_count'] = len(text)
        
        # Extract skills
        analysis['skills'] = self._extract_skills(text)
        
        # Extract experience
        analysis['experience'] = self._extract_experience(text)
        
        # Extract education
        analysis['education'] = self._extract_education(text)
        
        # Calculate scores
        analysis['scores'] = self._calculate_scores(text, analysis['skills'])
        
        # Generate recommendations
        analysis['recommendations'] = self._generate_recommendations(analysis)
        
        return analysis
    
    def _extract_skills(self, text):
        text_lower = text.lower()
        found_skills = {}
        
        for category, skills in self.skill_categories.items():
            category_skills = []
            for skill in skills:
                if skill in text_lower:
                    category_skills.append(skill.title())
            
            if category_skills:
                found_skills[category] = category_skills
        
        return found_skills
    
    def _extract_experience(self, text):
        experience = {}
        
        # Extract years of experience
        years_pattern = r'(\d+)\s*(?:\+)?\s*years?(?:\s+of)?\s*experience'
        match = re.search(years_pattern, text, re.IGNORECASE)
        experience['years'] = match.group(1) if match else "Not specified"
        
        return experience
    
    def _extract_education(self, text):
        education = {}
        
        # Extract degrees
        degrees = ['bachelor', 'master', 'phd', 'mba', 'b\.?tech', 'm\.?tech', 'b\.?e', 'm\.?e']
        degree_pattern = r'\b(' + '|'.join(degrees) + r')\b'
        matches = re.findall(degree_pattern, text, re.IGNORECASE)
        education['degrees'] = list(set(matches))
        
        return education
    
    def _calculate_scores(self, text, skills):
        scores = {}
        
        # Skills score
        total_skills = sum(len(skills_list) for skills_list in skills.values())
        scores['skills_score'] = min(10, total_skills / 2)  # Normalize to 10
        
        # Experience score
        exp_score = 0
        if any(str(i) in text for i in range(1, 6)):
            exp_score = min(10, 5)  # Basic score
        scores['experience_score'] = exp_score
        
        # Education score
        edu_score = min(10, len(self._extract_education(text)['degrees']) * 3)
        scores['education_score'] = edu_score
        
        # Overall score
        scores['overall_score'] = (scores['skills_score'] + scores['experience_score'] + scores['education_score']) / 3
        
        return scores
    
    def _generate_recommendations(self, analysis):
        recommendations = []
        scores = analysis['scores']
        
        if scores['skills_score'] < 6:
            recommendations.append("Consider adding more technical skills to your resume")
        
        if scores['experience_score'] < 5:
            recommendations.append("Highlight your work experience with specific achievements")
        
        if analysis['word_count'] < 200:
            recommendations.append("Your resume seems brief. Consider adding more details about your projects and achievements")
        
        if not recommendations:
            recommendations.append("Your resume looks strong! Focus on preparing for behavioral questions")
        
        return recommendations