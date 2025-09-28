#!/usr/bin/env python3
import os
import nltk
import sys

def setup_project():
    print("Setting up AI Interview Project...")
    
    # Create necessary directories
    directories = [
        'static/css',
        'static/js', 
        'static/images',
        'templates',
        'models',
        'utils',
        'data/questions',
        'data/responses',
        'uploads/resumes'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"Created directory: {directory}")
    
    # Create __init__.py files
    init_files = ['models/__init__.py', 'utils/__init__.py']
    for init_file in init_files:
        with open(init_file, 'w') as f:
            f.write('# Package initialization\n')
        print(f"Created: {init_file}")
    
    # Download NLTK data
    print("Downloading NLTK data...")
    try:
        nltk.download('punkt', quiet=True)
        print("NLTK setup completed successfully!")
    except Exception as e:
        print(f"Warning: NLTK download failed: {e}")
    
    print("\nSetup completed! You can now run: python app.py")

if __name__ == '__main__':
    setup_project()