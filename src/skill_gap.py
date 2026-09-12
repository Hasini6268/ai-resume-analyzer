# =========================================================
# SKILL GAP ANALYSIS
# =========================================================


def calculate_skill_gap(
    required_skills,
    resume_skills,
    job_relevance=None
):
    """
    Calculate missing skills and prioritize them
    using job relevance information.
    """

    # -----------------------------------------------------
    # NORMALIZE SKILLS
    # -----------------------------------------------------

    required = [
        skill.lower().strip()
        for skill in required_skills
    ]

    resume = [
        skill.lower().strip()
        for skill in resume_skills
    ]

    # Remove duplicates while preserving order
    required = list(dict.fromkeys(required))
    resume = list(dict.fromkeys(resume))

    # -----------------------------------------------------
    # MATCHED SKILLS
    # -----------------------------------------------------

    matched_skills = []

    for skill in required:

        if skill in resume:
            matched_skills.append(skill)

    # -----------------------------------------------------
    # MISSING SKILLS
    # -----------------------------------------------------

    missing_skills = []

    for skill in required:

        if skill not in resume:
            missing_skills.append(skill)

    # -----------------------------------------------------
    # PERCENTAGES
    # -----------------------------------------------------

    total_required = len(required)

    if total_required == 0:

        gap_percentage = 0
        match_percentage = 0

    else:

        gap_percentage = round(
            (len(missing_skills) / total_required) * 100
        )

        match_percentage = round(
            (len(matched_skills) / total_required) * 100
        )

    # -----------------------------------------------------
    # PRIORITIZE MISSING SKILLS
    # -----------------------------------------------------

    prioritized_missing = []

    for skill in missing_skills:

        priority = get_skill_priority(
            skill,
            job_relevance
        )

        prioritized_missing.append({

            "skill": skill,

            "priority": priority

        })

    # -----------------------------------------------------
    # FINAL RESULT
    # -----------------------------------------------------

    return {

        "matched_skills":
            matched_skills,

        "missing_skills":
            missing_skills,

        "match_percentage":
            match_percentage,

        "gap_percentage":
            gap_percentage,

        "prioritized_missing_skills":
            prioritized_missing

    }


# =========================================================
# GET SKILL PRIORITY
# =========================================================

def get_skill_priority(
    skill,
    job_relevance=None
):
    """
    Determine whether a missing skill is High,
    Medium or Low priority.

    job_relevance from job_matcher.py is a LIST,
    not a dictionary.
    """

    skill = skill.lower().strip()

    # -----------------------------------------------------
    # NO JOB RELEVANCE DATA
    # -----------------------------------------------------

    if not job_relevance:

        return "Medium"

    # -----------------------------------------------------
    # HANDLE JOB RELEVANCE LIST
    # -----------------------------------------------------

    if isinstance(job_relevance, list):

        for item in job_relevance:

            if not isinstance(item, dict):
                continue

            item_skill = str(
                item.get("skill", "")
            ).lower().strip()

            if item_skill != skill:
                continue

            # ---------------------------------------------
            # CHECK NUMERIC SCORE
            # ---------------------------------------------

            score = item.get("score")

            if isinstance(score, (int, float)):

                if score >= 70:
                    return "High"

                elif score >= 40:
                    return "Medium"

                else:
                    return "Low"

            # ---------------------------------------------
            # CHECK RELEVANCE TEXT
            # ---------------------------------------------

            relevance = str(
                item.get("relevance", "")
            ).lower()

            if "high" in relevance:

                return "High"

            elif "moderate" in relevance:

                return "Medium"

            elif "low" in relevance:

                return "Low"

            elif "missing" in relevance:

                return "High"

    # -----------------------------------------------------
    # HANDLE DICTIONARY
    # -----------------------------------------------------

    if isinstance(job_relevance, dict):

        relevance = job_relevance.get(skill)

        if isinstance(relevance, dict):

            score = relevance.get(
                "score",
                0
            )

            if score >= 70:
                return "High"

            elif score >= 40:
                return "Medium"

            else:
                return "Low"

        elif isinstance(
            relevance,
            (int, float)
        ):

            if relevance >= 70:
                return "High"

            elif relevance >= 40:
                return "Medium"

            else:
                return "Low"

    # -----------------------------------------------------
    # DEFAULT
    # -----------------------------------------------------

    return "Medium"


# =========================================================
# HIGH PRIORITY GAPS
# =========================================================

def get_high_priority_gaps(
    skill_gap_result
):
    """
    Return only high-priority missing skills.
    """

    return [

        item["skill"]

        for item in skill_gap_result.get(
            "prioritized_missing_skills",
            []
        )

        if item.get("priority") == "High"

    ]


# =========================================================
# LEARNING ORDER
# =========================================================

def get_learning_order(
    skill_gap_result
):
    """
    Sort missing skills according to priority.
    """

    priority_order = {

        "High": 1,

        "Medium": 2,

        "Low": 3

    }

    skills = skill_gap_result.get(
        "prioritized_missing_skills",
        []
    )

    return sorted(

        skills,

        key=lambda item:
        priority_order.get(
            item.get("priority"),
            4
        )

    )