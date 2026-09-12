import re


# Skills that the system can detect
SKILLS = [
    "Python",
    "Java",
    "C++",
    "C",
    "SQL",
    "HTML",
    "CSS",
    "JavaScript",
    "MySQL",
    "GitHub",
    "Machine Learning",
    "AI"
]


def extract_skills(text):

    detected_skills = []

    text_lower = text.lower()

    for skill in SKILLS:

        # Exact word/phrase matching
        pattern = r"\b" + re.escape(skill.lower()) + r"\b"

        if re.search(pattern, text_lower):

            detected_skills.append(skill)

    return detected_skills