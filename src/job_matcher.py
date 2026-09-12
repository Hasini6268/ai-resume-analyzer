# ==================================================
# JOB RELEVANCE ANALYZER
# ==================================================


def calculate_job_relevance(
    required_skills,
    resume_skills,
    evidence_results
):

    relevance_results = []

    # ----------------------------------------------
    # Normalize resume skills
    # ----------------------------------------------

    normalized_resume_skills = [
        str(skill).lower().strip()
        for skill in resume_skills
    ]

    # ----------------------------------------------
    # Normalize evidence results
    # ----------------------------------------------

    normalized_evidence_results = []

    for item in evidence_results:

        normalized_item = dict(item)

        normalized_item["skill"] = (
            str(item.get("skill", ""))
            .lower()
            .strip()
        )

        normalized_evidence_results.append(
            normalized_item
        )

    # ----------------------------------------------
    # Analyze each required job skill
    # ----------------------------------------------

    for original_skill in required_skills:

        skill = str(original_skill).lower().strip()

        # ------------------------------------------
        # Skill is present in resume
        # ------------------------------------------

        if skill in normalized_resume_skills:

            # Find evidence information
            evidence = next(
                (
                    item
                    for item in normalized_evidence_results
                    if item["skill"] == skill
                ),
                None
            )

            # --------------------------------------
            # Evidence found
            # --------------------------------------

            if evidence:

                evidence_score = float(
                    evidence.get(
                        "evidence_score",
                        0
                    )
                )

                # Keep the REAL evidence score
                relevance_score = round(
                    evidence_score
                )

                # ----------------------------------
                # HIGH JOB RELEVANCE
                # ----------------------------------

                if evidence_score >= 80:

                    relevance = "High Job Relevance"

                    reason = (
                        f"{skill} is required by the job "
                        f"and has strong supporting evidence "
                        f"in the resume."
                    )

                # ----------------------------------
                # MODERATE JOB RELEVANCE
                # ----------------------------------

                elif evidence_score >= 50:

                    relevance = "Moderate Job Relevance"

                    reason = (
                        f"{skill} is required by the job "
                        f"and has moderate supporting evidence "
                        f"in the resume."
                    )

                # ----------------------------------
                # LOW JOB RELEVANCE
                # ----------------------------------

                else:

                    relevance = "Low Job Relevance"

                    reason = (
                        f"{skill} is required by the job "
                        f"but has limited supporting evidence "
                        f"in the resume."
                    )

            # --------------------------------------
            # Skill exists but evidence unavailable
            # --------------------------------------

            else:

                relevance = "Low Job Relevance"

                relevance_score = 30

                reason = (
                    f"{skill} is present in the resume, "
                    f"but supporting evidence could not "
                    f"be evaluated."
                )

        # ------------------------------------------
        # Skill is missing from resume
        # ------------------------------------------

        else:

            relevance = "Missing Skill"

            relevance_score = 0

            reason = (
                f"{skill} is required by the job "
                f"but was not detected in the resume."
            )

        # ------------------------------------------
        # Store result
        # ------------------------------------------

        relevance_results.append({

            "skill": skill,

            "relevance": relevance,

            "relevance_score": relevance_score,

            "reason": reason

        })

    return relevance_results