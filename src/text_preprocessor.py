import re


# =========================================================
# TEXT PREPROCESSOR
# AI RESUME ANALYZER
# =========================================================


def clean_text(text):
    """
    Clean and normalize resume or job-description text.
    """

    if not text:
        return ""

    # Convert to string
    text = str(text)

    # Convert to lowercase
    text = text.lower()

    # Replace common symbols with spaces
    text = re.sub(r"[/|•·]", " ", text)

    # Keep useful programming symbols such as + and #
    text = re.sub(r"[^a-z0-9+#.\-\s]", " ", text)

    # Remove extra spaces
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def normalize_skill_names(text):
    """
    Normalize common abbreviations and alternative
    names used for technical skills.
    """

    text = clean_text(text)

    skill_variations = {

        # Programming
        "py": "python",
        "python3": "python",
        "java programming": "java",
        "c programming": "c",
        "c language": "c",
        "c plus plus": "c++",
        "cpp": "c++",

        # Web development
        "js": "javascript",
        "javascript programming": "javascript",
        "html5": "html",
        "css3": "css",

        # Database
        "structured query language": "sql",
        "mysql database": "mysql",
        "sql database": "sql",

        # AI / ML
        "ml": "machine learning",
        "machine-learning": "machine learning",
        "artificial intelligence": "ai",
        "natural language processing": "nlp",
        "deep-learning": "deep learning",
        "dl": "deep learning",

        # Version control
        "git hub": "github",
        "version control": "git",

        # Data structures
        "data structure": "data structures",
        "dsa": "data structures",
        "data structures and algorithms":
            "data structures"
    }

    # Replace longer expressions first
    for old_name, new_name in sorted(
        skill_variations.items(),
        key=lambda item: len(item[0]),
        reverse=True
    ):
        pattern = r"\b" + re.escape(old_name) + r"\b"
        text = re.sub(pattern, new_name, text)

    return text


def preprocess_text(text):
    """
    Complete preprocessing pipeline.

    1. Clean text
    2. Normalize skill names
    """

    text = clean_text(text)
    text = normalize_skill_names(text)

    return text


def tokenize_text(text):
    """
    Convert preprocessed text into individual words.
    """

    text = preprocess_text(text)

    if not text:
        return []

    return text.split()


def contains_phrase(text, phrase):
    """
    Check whether a phrase exists in the text.
    """

    text = preprocess_text(text)
    phrase = preprocess_text(phrase)

    if not text or not phrase:
        return False

    return phrase in text