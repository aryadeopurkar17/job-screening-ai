# matcher.py
from sklearn.feature_extraction.text import TfidfVectorizer

# Define SYNONYM_MAP globally (outside functions)
SYNONYM_MAP = {
    "postgresql": "sql",
    "postgres": "sql",
    "pytorch": "machine learning",
    "tensorflow": "machine learning",
    "aws": "cloud computing",
    "gcp": "cloud computing",
    "azure": "cloud computing"
}


def calculate_match_score(job_skills, candidate_skills):
    def process_skills(skills):
        processed = []
        for skill in skills.replace(",", " ").split():
            skill_lower = skill.strip().lower()
            mapped_skill = SYNONYM_MAP.get(skill_lower, skill_lower)  # Now accessible
            processed.append(mapped_skill)
        return list(set(processed))

    job_skills_clean = process_skills(job_skills)
    candidate_skills_clean = process_skills(candidate_skills)

    # Calculate score as (matched job skills / total job skills) * 100
    job_set = set(job_skills_clean)
    candidate_set = set(candidate_skills_clean)
    intersection = job_set.intersection(candidate_set)

    return round((len(intersection) / len(job_set)) * 100, 2) if job_set else 0.0