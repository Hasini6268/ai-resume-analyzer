# ============================================================
# EVIDENCE-BASED SKILL ANALYZER
# ============================================================

import re


# ============================================================
# ACTION WORDS
# ============================================================

ACTION_WORDS = [
    "developed",
    "develop",
    "implemented",
    "implement",
    "built",
    "build",
    "created",
    "create",
    "designed",
    "design",
    "programmed",
    "used",
    "using",
    "worked",
    "working",
    "applied",
    "integrated",
    "tested",
    "deployed",
    "analyzed",
    "managed",
    "maintained",
    "configured",
    "automated",
    "trained",
    "optimized",
    "solved",
    "developing",
    "testing",
    "integrating"
]


# ============================================================
# EVIDENCE SECTIONS
# ============================================================

EVIDENCE_SECTIONS = {

    "Project": [
        "project",
        "projects",
        "academic project",
        "mini project",
        "major project",
        "final year project"
    ],

    "Experience": [
        "experience",
        "work experience",
        "internship",
        "internships",
        "employment",
        "professional experience"
    ],

    "Certification": [
        "certification",
        "certifications",
        "certificate",
        "certificates"
    ],

    "Education": [
        "education",
        "qualification",
        "degree",
        "academic",
        "coursework"
    ]
}


# ============================================================
# NORMALIZE TEXT
# ============================================================

def normalize_text(text):

    if not text:
        return ""

    text = str(text).lower()

    # Replace multiple spaces and new lines
    text = re.sub(r"\s+", " ", text)

    return text.strip()


# ============================================================
# GET SKILL REGEX PATTERN
# ============================================================

def get_skill_pattern(skill):

    skill_lower = normalize_text(skill)

    # Special handling for C++
    if skill_lower in ["c++", "cpp"]:

        return r"(?<!\w)c\+\+(?!\w)"

    # Special handling for C
    if skill_lower == "c":

        return r"(?<!\w)c(?!\w)"

    # Normal skills
    return (
        r"(?<!\w)"
        + re.escape(skill_lower)
        + r"(?!\w)"
    )


# ============================================================
# FIND SKILL IN TEXT
# ============================================================

def skill_in_text(skill, text):

    if not skill or not text:
        return False

    pattern = get_skill_pattern(skill)

    return bool(
        re.search(
            pattern,
            text,
            re.IGNORECASE
        )
    )


# ============================================================
# FIND SKILL POSITIONS
# ============================================================

def find_skill_positions(skill, text):

    if not skill or not text:
        return []

    pattern = get_skill_pattern(skill)

    positions = []

    for match in re.finditer(
        pattern,
        text,
        re.IGNORECASE
    ):

        positions.append(
            match.start()
        )

    return positions


# ============================================================
# CHECK ACTION EVIDENCE
# ============================================================

def has_action_evidence(
    skill,
    text,
    window=180
):

    positions = find_skill_positions(
        skill,
        text
    )

    for position in positions:

        start = max(
            0,
            position - window
        )

        end = min(
            len(text),
            position + window
        )

        surrounding_text = text[
            start:end
        ]

        for action in ACTION_WORDS:

            action_pattern = (
                r"(?<!\w)"
                + re.escape(action)
                + r"(?!\w)"
            )

            if re.search(
                action_pattern,
                surrounding_text,
                re.IGNORECASE
            ):

                return True

    return False


# ============================================================
# FIND SECTION EVIDENCE
# ============================================================

def find_section_evidence(
    skill,
    resume_text
):

    evidence_found = []

    for section_name, keywords in EVIDENCE_SECTIONS.items():

        section_detected = False

        for keyword in keywords:

            keyword_pattern = (
                r"(?<!\w)"
                + re.escape(keyword)
                + r"(?!\w)"
            )

            matches = re.finditer(
                keyword_pattern,
                resume_text,
                re.IGNORECASE
            )

            for match in matches:

                # Look around the section heading
                start = max(
                    0,
                    match.start() - 100
                )

                end = min(
                    len(resume_text),
                    match.end() + 1200
                )

                section_text = resume_text[
                    start:end
                ]

                if skill_in_text(
                    skill,
                    section_text
                ):

                    section_detected = True
                    break

            if section_detected:
                break

        if section_detected:

            evidence_found.append(
                section_name
            )

    return evidence_found


# ============================================================
# COUNT EVIDENCE TYPES
# ============================================================

def get_evidence_count(evidence_found):

    if not evidence_found:
        return 0

    return len(
        set(evidence_found)
    )


# ============================================================
# CALCULATE EVIDENCE SCORE
# ============================================================

def calculate_evidence_score(
    evidence_found,
    action_evidence
):

    # Base score for a skill being detected
    score = 10

    # Strong practical evidence
    if "Project" in evidence_found:
        score += 30

    if "Experience" in evidence_found:
        score += 30

    # Supporting evidence
    if "Certification" in evidence_found:
        score += 15

    if "Education" in evidence_found:
        score += 5

    # Action-based evidence
    if action_evidence:
        score += 10

    # Additional confidence when evidence
    # appears in multiple sections
    if get_evidence_count(evidence_found) >= 2:
        score += 5

    # Maximum score
    score = min(
        score,
        100
    )

    return score


# ============================================================
# DETERMINE EVIDENCE STRENGTH
# ============================================================

def get_evidence_strength(score):

    if score >= 80:

        return "Strong Evidence"

    elif score >= 50:

        return "Moderate Evidence"

    else:

        return "Weak Evidence"


# ============================================================
# GENERATE EXPLANATION
# ============================================================

def generate_reason(
    skill,
    evidence_found,
    action_evidence,
    score
):

    evidence_text = ", ".join(
        evidence_found
    )

    # --------------------------------------------------------
    # STRONG EVIDENCE
    # --------------------------------------------------------

    if score >= 80:

        if evidence_text:

            action_text = ""

            if action_evidence:
                action_text = (
                    " and action-based evidence"
                )

            return (
                f"{skill} has strong supporting evidence "
                f"through {evidence_text.lower()} evidence"
                f"{action_text}."
            )

        return (
            f"{skill} has strong supporting evidence "
            f"in the resume."
        )

    # --------------------------------------------------------
    # MODERATE EVIDENCE
    # --------------------------------------------------------

    elif score >= 50:

        if evidence_text:

            return (
                f"{skill} is supported by "
                f"{evidence_text.lower()} evidence, "
                f"but stronger practical evidence could "
                f"increase confidence."
            )

        return (
            f"{skill} has some supporting evidence, "
            f"but additional practical evidence is needed."
        )

    # --------------------------------------------------------
    # WEAK EVIDENCE
    # --------------------------------------------------------

    else:

        if evidence_text:

            return (
                f"{skill} is mentioned in the resume, "
                f"but the available {evidence_text.lower()} "
                f"evidence is limited."
            )

        return (
            f"{skill} is mentioned in the resume, "
            f"but sufficient supporting evidence "
            f"was not identified."
        )


# ============================================================
# ANALYZE SKILL EVIDENCE
# ============================================================

def analyze_skill_evidence(
    resume_text,
    resume_skills
):

    # Normalize resume
    resume_text = normalize_text(
        resume_text
    )

    evidence_results = []

    # Analyze every detected skill
    for skill in resume_skills:

        # ----------------------------------------------------
        # 1. Find evidence sections
        # ----------------------------------------------------

        evidence_found = find_section_evidence(
            skill,
            resume_text
        )

        # ----------------------------------------------------
        # 2. Check action words
        # ----------------------------------------------------

        action_evidence = has_action_evidence(
            skill,
            resume_text
        )

        # ----------------------------------------------------
        # 3. Calculate evidence score
        # ----------------------------------------------------

        evidence_score = calculate_evidence_score(
            evidence_found,
            action_evidence
        )

        # ----------------------------------------------------
        # 4. Determine evidence strength
        # ----------------------------------------------------

        strength = get_evidence_strength(
            evidence_score
        )

        # ----------------------------------------------------
        # 5. Generate explanation
        # ----------------------------------------------------

        reason = generate_reason(
            skill,
            evidence_found,
            action_evidence,
            evidence_score
        )

        # ----------------------------------------------------
        # 6. Store result
        # ----------------------------------------------------

        evidence_results.append({

            "skill": skill,

            "evidence": evidence_found,

            "strength": strength,

            "evidence_score": evidence_score,

            "action_evidence": action_evidence,

            "reason": reason

        })

    return evidence_results