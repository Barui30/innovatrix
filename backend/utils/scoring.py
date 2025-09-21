from fuzzywuzzy import fuzz
from sentence_transformers import SentenceTransformer, util

# Load the Sentence-BERT model once
sbert_model = SentenceTransformer('all-MiniLM-L6-v2')

def hard_match_score(resume_text, jd_text, skills_list):
    """
    Calculates a hard match score based on the presence of skills.
    Returns a score out of 50.
    """
    score = 0
    for skill in skills_list:
        if skill.lower() in resume_text.lower():
            score += 1
    return (score / len(skills_list)) * 50  # weight: 50% for hard match

def semantic_score(resume_text, jd_text):
    """
    Calculates semantic similarity between resume and job description using Sentence-BERT.
    Returns a score out of 50.
    """
    embeddings1 = sbert_model.encode(resume_text, convert_to_tensor=True)
    embeddings2 = sbert_model.encode(jd_text, convert_to_tensor=True)
    similarity = util.cos_sim(embeddings1, embeddings2)
    return float(similarity[0][0]) * 50  # weight: 50% for soft match

def extract_missing_skills(resume_text, skills_list):
    """
    Returns a list of skills that are missing from the resume.
    """
    return [skill for skill in skills_list if skill.lower() not in resume_text.lower()]

def final_score(resume_text, jd_text, skills_list):
    """
    Calculates the final score combining hard match and semantic similarity.
    Returns:
        total (float): final score out of 100
        verdict (str): High / Medium / Low
        missing_skills (list): list of missing skills
        feedback (str): feedback message
    """
    hard = hard_match_score(resume_text, jd_text, skills_list)
    soft = semantic_score(resume_text, jd_text)
    total = hard + soft

    if total >= 80:
        verdict = "High"
    elif total >= 50:
        verdict = "Medium"
    else:
        verdict = "Low"

    missing_skills = extract_missing_skills(resume_text, skills_list)
    feedback = f"Improve these skills: {', '.join(missing_skills)}" if missing_skills else "Great!"
    
    return total, verdict, missing_skills, feedback
