# resume_parser.py - Enhanced resume parsing to extract detailed features for better matching

import spacy
import re

# Load English tokenizer, POS tagger, parser, NER and word vectors
nlp = spacy.load("en_core_web_sm")

def parse_resume_text(text):
    """
    Parse the resume text to extract skills, education, experience, and other features.

    Args:
        text (str): Full text extracted from resume PDF.

    Returns:
        dict: Parsed data including skills, education, experience, years of experience, education level, and full text.
    """
    doc = nlp(text)

    # Define a list of skills to look for (expand as needed)
    skills_list = ["python", "java", "c++", "machine learning", "data analysis", "nlp", "sql", "javascript", "flask", "django", "react"]
    skills_found = set()

    text_lower = text.lower()
    for skill in skills_list:
        if skill in text_lower:
            skills_found.add(skill)

    # Extract education sentences using simple heuristics
    education = []
    education_levels = {"phd": 4, "doctorate": 4, "master": 3, "bachelor": 2, "associate": 1}
    education_level_score = 0
    for sent in doc.sents:
        sent_lower = sent.text.lower()
        if "university" in sent_lower or any(level in sent_lower for level in education_levels.keys()):
            education.append(sent.text.strip())
            for level, score in education_levels.items():
                if level in sent_lower and score > education_level_score:
                    education_level_score = score

    # Extract years of experience by searching for patterns like "X years"
    experience_years = 0
    experience = []
    years_pattern = re.compile(r"(\d+)\s+years?")
    matches = years_pattern.findall(text_lower)
    if matches:
        experience_years = max(int(y) for y in matches)
        experience.append(f"Years of experience mentioned: {experience_years}")

    # Extract experience summary by searching for years mentioned (basic)
    years_mentioned = re.findall(r"\b(19|20)\d{2}\b", text)
    if years_mentioned:
        experience.append(f"Years mentioned: {', '.join(set(years_mentioned))}")

    return {
        "skills": list(skills_found),
        "education": education,
        "education_level_score": education_level_score,
        "experience": experience,
        "experience_years": experience_years,
        "full_text": text
    }
