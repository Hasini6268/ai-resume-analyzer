from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import pymupdf

from src.evidence_analyzer import analyze_skill_evidence
from src.job_matcher import calculate_job_relevance
from src.skill_extractor import extract_skills
from src.text_preprocessor import preprocess_text
from src.skill_gap import calculate_skill_gap
from src.recommender import generate_recommendations


# =========================================================
# FLASK APPLICATION
# =========================================================

app = Flask(__name__)
CORS(app)


# =========================================================
# HOME ROUTE
# =========================================================

@app.route("/")
def home():
    """
    Serve the main AI Resume Analyzer frontend.
    """
    return send_from_directory(".", "index.html")


# =========================================================
# RESULTS PAGE
# =========================================================

@app.route("/results.html")
def results_page():
    """
    Serve the resume analysis results page.
    """
    return send_from_directory(".", "results.html")


# =========================================================
# RESUME BUILDER PAGE
# =========================================================

@app.route("/resume_builder.html")
def resume_builder_page():
    """
    Serve the Evidence-Aware Resume Builder page.
    """
    return send_from_directory(".", "resume_builder.html")


# =========================================================
# HEALTH CHECK ROUTE
# =========================================================

@app.route("/health")
def health():
    """
    Simple health-check endpoint for deployment platforms.
    """
    return jsonify({
        "status": "healthy",
        "message": "AI Resume Analyzer is running!"
    })


# =========================================================
# RESUME ANALYSIS ROUTE
# =========================================================

@app.route("/analyze", methods=["POST"])
def analyze():

    # -----------------------------------------------------
    # GET INPUTS
    # -----------------------------------------------------

    resume = request.files.get("resume")

    job_description = request.form.get(
        "job_description",
        ""
    )

    # -----------------------------------------------------
    # VALIDATION
    # -----------------------------------------------------

    if not resume:
        return jsonify({
            "error": "Please upload a resume PDF."
        }), 400

    if not job_description.strip():
        return jsonify({
            "error": "Please enter the job description."
        }), 400

    # -----------------------------------------------------
    # READ RESUME PDF
    # -----------------------------------------------------

    try:

        file_data = resume.read()

        if not file_data:
            return jsonify({
                "error": "The uploaded PDF is empty."
            }), 400

        document = pymupdf.open(
            stream=file_data,
            filetype="pdf"
        )

        resume_text = ""

        for page in document:
            resume_text += page.get_text()

        document.close()

        if not resume_text.strip():
            return jsonify({
                "error": "Could not extract text from the PDF."
            }), 400

    except Exception as e:

        return jsonify({
            "error": "Could not read the PDF.",
            "details": str(e)
        }), 400

    # -----------------------------------------------------
    # TEXT PREPROCESSING
    # -----------------------------------------------------

    try:

        processed_resume_text = preprocess_text(
            resume_text
        )

        processed_job_description = preprocess_text(
            job_description
        )

    except Exception as e:

        return jsonify({
            "error": "Text preprocessing failed.",
            "details": str(e)
        }), 500

    # -----------------------------------------------------
    # EXTRACT SKILLS
    # -----------------------------------------------------

    try:

        resume_skills = extract_skills(
            processed_resume_text
        )

        required_skills = extract_skills(
            processed_job_description
        )

    except Exception as e:

        return jsonify({
            "error": "Skill extraction failed.",
            "details": str(e)
        }), 500

    # -----------------------------------------------------
    # NORMALIZE SKILL NAMES
    # -----------------------------------------------------

    resume_skills = [
        str(skill).lower().strip()
        for skill in resume_skills
    ]

    required_skills = [
        str(skill).lower().strip()
        for skill in required_skills
    ]

    # -----------------------------------------------------
    # REMOVE DUPLICATES
    # -----------------------------------------------------

    resume_skills = list(
        dict.fromkeys(resume_skills)
    )

    required_skills = list(
        dict.fromkeys(required_skills)
    )

    # -----------------------------------------------------
    # INITIAL SKILL GAP ANALYSIS
    # -----------------------------------------------------

    try:

        skill_gap_result = calculate_skill_gap(
            required_skills,
            resume_skills
        )

        matched_skills = skill_gap_result.get(
            "matched_skills",
            []
        )

        missing_skills = skill_gap_result.get(
            "missing_skills",
            []
        )

    except Exception as e:

        return jsonify({
            "error": "Skill gap analysis failed.",
            "details": str(e)
        }), 500

    # -----------------------------------------------------
    # BASIC JOB MATCH SCORE
    # -----------------------------------------------------

    if required_skills:

        match_score = (
            len(matched_skills)
            / len(required_skills)
        ) * 100

    else:

        match_score = 0

    # -----------------------------------------------------
    # EVIDENCE-BASED SKILL ANALYSIS
    # -----------------------------------------------------

    try:

        # Original resume text is intentionally used here.
        #
        # Evidence detection depends on:
        # - Projects
        # - Experience
        # - Certifications
        # - Education
        # - Action words
        # - Supporting descriptions

        evidence_results = analyze_skill_evidence(
            resume_text,
            resume_skills
        )

    except Exception as e:

        return jsonify({
            "error": "Evidence analysis failed.",
            "details": str(e)
        }), 500

    # -----------------------------------------------------
    # JOB RELEVANCE ANALYSIS
    # -----------------------------------------------------

    try:

        job_relevance = calculate_job_relevance(
            required_skills,
            resume_skills,
            evidence_results
        )

    except Exception as e:

        return jsonify({
            "error": "Job relevance calculation failed.",
            "details": str(e)
        }), 500

    # -----------------------------------------------------
    # UPDATE SKILL GAP PRIORITIES
    # -----------------------------------------------------

    try:

        skill_gap_result = calculate_skill_gap(
            required_skills,
            resume_skills,
            job_relevance
        )

    except Exception as e:

        return jsonify({
            "error": "Skill priority calculation failed.",
            "details": str(e)
        }), 500

    # =====================================================
    # EVIDENCE-AWARE JOB FIT
    # =====================================================
    #
    # Basic Job Match:
    #     Percentage of required skills found.
    #
    # Evidence Quality:
    #     Strength of supporting evidence for matched skills.
    #
    # Formula:
    #
    #     Evidence Quality Factor =
    #         Average Evidence Score / 100
    #
    #     Evidence-Aware Job Fit =
    #         Basic Job Match * Evidence Quality Factor
    #
    # Example:
    #
    #     Basic Match = 64%
    #     Average Evidence = 56%
    #
    #     Evidence-Aware Fit =
    #         64 * 0.56 = approximately 36%
    #
    # Evidence is not multiplied by job relevance again,
    # because job relevance is already derived from evidence.
    #
    # =====================================================

    evidence_aware_components = []

    matched_evidence_scores = []

    for skill in required_skills:

        # ---------------------------------------------
        # Find job relevance information
        # ---------------------------------------------

        relevance_item = next(
            (
                item
                for item in job_relevance
                if str(
                    item.get("skill", "")
                ).lower().strip() == skill
            ),
            None
        )

        # ---------------------------------------------
        # Find evidence information
        # ---------------------------------------------

        evidence_item = next(
            (
                item
                for item in evidence_results
                if str(
                    item.get("skill", "")
                ).lower().strip() == skill
            ),
            None
        )

        # ---------------------------------------------
        # Missing skill
        # ---------------------------------------------

        if skill not in resume_skills:

            evidence_aware_components.append({

                "skill": skill,

                "evidence_score": 0,

                "relevance_score": 0,

                "component_score": 0

            })

            continue

        # ---------------------------------------------
        # Get evidence score
        # ---------------------------------------------

        evidence_score = 0

        if evidence_item:

            try:

                evidence_score = float(
                    evidence_item.get(
                        "evidence_score",
                        0
                    )
                )

            except (
                TypeError,
                ValueError
            ):

                evidence_score = 0

            matched_evidence_scores.append(
                evidence_score
            )

        # ---------------------------------------------
        # Get relevance score
        # ---------------------------------------------

        relevance_score = 0

        if relevance_item:

            try:

                relevance_score = float(
                    relevance_item.get(
                        "relevance_score",
                        0
                    )
                )

            except (
                TypeError,
                ValueError
            ):

                relevance_score = 0

        # ---------------------------------------------
        # Component score
        # ---------------------------------------------

        component_score = evidence_score

        evidence_aware_components.append({

            "skill": skill,

            "evidence_score":
                round(evidence_score),

            "relevance_score":
                round(relevance_score),

            "component_score":
                round(component_score)

        })

    # -----------------------------------------------------
    # AVERAGE EVIDENCE SCORE
    # -----------------------------------------------------

    if matched_evidence_scores:

        average_evidence_score = (
            sum(matched_evidence_scores)
            / len(matched_evidence_scores)
        )

    else:

        average_evidence_score = 0

    # -----------------------------------------------------
    # EVIDENCE QUALITY FACTOR
    # -----------------------------------------------------

    evidence_quality_factor = (
        average_evidence_score / 100
    )

    # -----------------------------------------------------
    # FINAL EVIDENCE-AWARE JOB FIT
    # -----------------------------------------------------

    evidence_aware_score = (
        match_score
        * evidence_quality_factor
    )

    # -----------------------------------------------------
    # EVIDENCE COVERAGE
    # -----------------------------------------------------

    if required_skills:

        evidence_coverage = (
            len(matched_evidence_scores)
            / len(required_skills)
        ) * 100

    else:

        evidence_coverage = 0

    # -----------------------------------------------------
    # PERSONALIZED LEARNING RECOMMENDATIONS
    # -----------------------------------------------------

    try:

        recommendations = generate_recommendations(
            missing_skills,
            skill_gap_result
        )

    except Exception as e:

        return jsonify({
            "error": "Recommendation generation failed.",
            "details": str(e)
        }), 500

    # -----------------------------------------------------
    # EVIDENCE STRENGTH SUMMARY
    # -----------------------------------------------------

    strong_skills = []

    moderate_skills = []

    weak_skills = []

    for item in evidence_results:

        score = item.get(
            "evidence_score",
            0
        )

        skill = item.get(
            "skill",
            ""
        )

        try:
            score = float(score)
        except (
            TypeError,
            ValueError
        ):
            score = 0

        if score >= 80:

            strong_skills.append(skill)

        elif score >= 50:

            moderate_skills.append(skill)

        else:

            weak_skills.append(skill)

    # -----------------------------------------------------
    # HIGH PRIORITY SKILL GAPS
    # -----------------------------------------------------

    high_priority_gaps = []

    for item in skill_gap_result.get(
        "prioritized_missing_skills",
        []
    ):

        if item.get("priority") == "High":

            high_priority_gaps.append(
                item.get("skill")
            )

    # -----------------------------------------------------
    # LEARNING ORDER
    # -----------------------------------------------------

    learning_order = []

    priority_order = {
        "High": 1,
        "Medium": 2,
        "Low": 3
    }

    prioritized_skills = skill_gap_result.get(
        "prioritized_missing_skills",
        []
    )

    sorted_skills = sorted(
        prioritized_skills,
        key=lambda item: priority_order.get(
            item.get("priority"),
            4
        )
    )

    for item in sorted_skills:

        learning_order.append({

            "skill":
                item.get("skill"),

            "priority":
                item.get("priority")

        })

    # =====================================================
    # EXPLAINABLE RESEARCH INSIGHT
    # =====================================================

    if evidence_aware_score >= 80:

        research_insight = (
            "The resume shows strong alignment with "
            "the job requirements and strong supporting "
            "evidence."
        )

    elif evidence_aware_score >= 60:

        research_insight = (
            "The resume shows good job alignment, "
            "but some required skills need stronger "
            "supporting evidence."
        )

    elif evidence_aware_score >= 40:

        research_insight = (
            "The resume contains several relevant "
            "skills, but missing skills and limited "
            "evidence reduce the overall job fit."
        )

    else:

        research_insight = (
            "The resume has limited evidence-based "
            "alignment with the job requirements. "
            "Developing missing skills and adding "
            "stronger project or experience evidence "
            "may improve job fit."
        )

    # -----------------------------------------------------
    # SKILL GAP EXPLANATION
    # -----------------------------------------------------

    total_required = len(required_skills)

    total_matched = len(matched_skills)

    total_missing = len(missing_skills)

    skill_gap_explanation = (

        f"The job requires {total_required} identified "
        f"skills. The resume demonstrates "
        f"{total_matched} of them and is missing "
        f"{total_missing}. The calculated skill gap "
        f"is {round(skill_gap_result.get('gap_percentage', 0))}%."

    )

    # =====================================================
    # FINAL JSON RESPONSE
    # =====================================================

    return jsonify({

        # -------------------------------------------------
        # STATUS
        # -------------------------------------------------

        "message":
            "Resume analyzed successfully!",

        # -------------------------------------------------
        # BASIC JOB MATCHING
        # -------------------------------------------------

        "match_score":
            round(match_score),

        # -------------------------------------------------
        # EVIDENCE-AWARE JOB FIT
        # -------------------------------------------------

        "evidence_aware_score":
            round(evidence_aware_score),

        "average_evidence_score":
            round(average_evidence_score),

        "evidence_quality_factor":
            round(
                evidence_quality_factor * 100
            ),

        "evidence_coverage":
            round(evidence_coverage),

        "evidence_aware_components":
            evidence_aware_components,

        # -------------------------------------------------
        # SKILLS
        # -------------------------------------------------

        "resume_skills":
            resume_skills,

        "required_skills":
            required_skills,

        "matched_skills":
            matched_skills,

        "missing_skills":
            missing_skills,

        # -------------------------------------------------
        # SKILL GAP ANALYSIS
        # -------------------------------------------------

        "skill_gap_percentage":
            round(
                skill_gap_result.get(
                    "gap_percentage",
                    0
                )
            ),

        "skill_match_percentage":
            round(
                skill_gap_result.get(
                    "match_percentage",
                    0
                )
            ),

        "prioritized_missing_skills":
            skill_gap_result.get(
                "prioritized_missing_skills",
                []
            ),

        "high_priority_gaps":
            high_priority_gaps,

        "learning_order":
            learning_order,

        "skill_gap_explanation":
            skill_gap_explanation,

        # -------------------------------------------------
        # EVIDENCE ANALYSIS
        # -------------------------------------------------

        "evidence_analysis":
            evidence_results,

        "strong_skills":
            strong_skills,

        "moderate_skills":
            moderate_skills,

        "weak_skills":
            weak_skills,

        # -------------------------------------------------
        # JOB RELEVANCE
        # -------------------------------------------------

        "job_relevance":
            job_relevance,

        # -------------------------------------------------
        # LEARNING RECOMMENDATIONS
        # -------------------------------------------------

        "learning_recommendations":
            recommendations,

        # -------------------------------------------------
        # EXPLAINABLE INSIGHT
        # -------------------------------------------------

        "research_insight":
            research_insight,

        # -------------------------------------------------
        # EXTRACTED RESUME TEXT
        # -------------------------------------------------

        "resume_text":
            resume_text

    })


# =========================================================
# START FLASK SERVER
# =========================================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )