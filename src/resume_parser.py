import pymupdf


def extract_text_from_pdf(file_path):
    """
    Extract text from a PDF resume.
    """

    document = pymupdf.open(file_path)

    text = ""

    for page in document:
        text += page.get_text()

    document.close()

    return text


if __name__ == "__main__":
    file_path = "data/resumes/sample_resume.pdf"

    resume_text = extract_text_from_pdf(file_path)

    print("----- EXTRACTED RESUME TEXT -----")
    print(resume_text)