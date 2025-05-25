# matcher.py - Match jobs to resume using TF-IDF vectorization and cosine similarity

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def match_jobs(resume_data, jobs):
    """
    Calculate match scores between resume and job descriptions with enhanced weighting and eligibility.

    Args:
        resume_data (dict): Parsed resume data including skills, education_level_score, experience_years, full_text.
        jobs (list): List of job dictionaries with descriptions.

    Returns:
        list: Jobs sorted by combined match score in descending order, each with 'match_score' and 'eligibility' keys.
    """
    resume_text = resume_data.get("full_text", "")
    resume_skills = set(resume_data.get("skills", []))
    resume_education_score = resume_data.get("education_level_score", 0)
    resume_experience_years = resume_data.get("experience_years", 0)

    job_descriptions = [job.get("description", "") for job in jobs]

    # Vectorize resume and job descriptions using TF-IDF
    vectorizer = TfidfVectorizer(stop_words='english')
    try:
        vectors = vectorizer.fit_transform([resume_text] + job_descriptions)
    except ValueError:
        # Handle empty vocabulary error
        for job in jobs:
            job["match_score"] = 0.0
            job["eligibility"] = "Insufficient data"
        return jobs

    resume_vector = vectors[0]
    job_vectors = vectors[1:]

    # Compute cosine similarity between resume and each job description
    similarities = cosine_similarity(resume_vector, job_vectors).flatten()

    enhanced_jobs = []
    for i, job in enumerate(jobs):
        # Basic text similarity score
        text_score = float(similarities[i]) * 100

        # Skill matching score (percentage of job skills found in resume)
        job_skills = set()
        # Extract skills from job description by simple keyword matching (can be improved)
        for skill in resume_skills:
            if skill in job.get("description", "").lower():
                job_skills.add(skill)
        skill_match_score = (len(job_skills) / len(resume_skills)) * 100 if resume_skills else 0

        # Education level match (simple heuristic: if resume education level >= 2 (Bachelor), add bonus)
        education_bonus = 10 if resume_education_score >= 2 else 0

        # Experience years match (if resume experience years >= 2, add bonus)
        experience_bonus = 10 if resume_experience_years >= 2 else 0

        # Combine scores with weights
        combined_score = (0.5 * text_score) + (0.3 * skill_match_score) + education_bonus + experience_bonus
        combined_score = min(combined_score, 100.0)  # Cap at 100%

        # Eligibility message based on combined score
        if combined_score >= 75:
            eligibility = "Highly Eligible"
        elif combined_score >= 50:
            eligibility = "Moderately Eligible"
        elif combined_score > 0:
            eligibility = "Low Eligibility"
        else:
            eligibility = "Insufficient data"

        job["match_score"] = round(combined_score, 2)
        job["eligibility"] = eligibility
        enhanced_jobs.append(job)

    # Sort jobs by combined match score descending
    jobs_sorted = sorted(enhanced_jobs, key=lambda x: x["match_score"], reverse=True)

    return jobs_sorted
