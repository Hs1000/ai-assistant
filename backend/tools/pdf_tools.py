import os
import re
from pypdf import PdfReader

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PDF_FOLDER = os.path.join(BASE_DIR, "data", "pdfs")


# -------------------------------
# CLEAN TEXT
# -------------------------------
def clean_text(text):
    return " ".join(text.split())


# -------------------------------
# EXTRACT KEYWORDS
# -------------------------------
def extract_keywords(query):
    clean_query = re.sub(r"[^\w\s]", "", query.lower())
    stopwords = {
        "what", "is", "the", "are", "in", "of", "a", "an", "to", "for", "on",
        "and", "or", "with", "from", "this", "that", "these", "those", "me",
        "show", "tell", "about"
    }
    return [w for w in clean_query.split() if w not in stopwords and len(w) > 1]


# -------------------------------
# SPLIT INTO SECTIONS (ROBUST)
# -------------------------------
def split_sections(text):
    """
    Splits text into {heading, content} sections by locating heading spans,
    then assigning content up to the next heading.
    """
    line_heading_pattern = r"^\s*([A-Z][A-Za-z&/\-\s]{2,60}:)\s*$"
    matches = list(re.finditer(line_heading_pattern, text, flags=re.MULTILINE))
    if not matches:
        # Fallback for PDFs that collapse line breaks in extraction.
        inline_heading_pattern = r"([A-Z][A-Za-z&/\-\s]{2,45}:)"
        matches = list(re.finditer(inline_heading_pattern, text))
    sections = []

    for idx, match in enumerate(matches):
        heading = match.group(1).strip()
        content_start = match.end()
        content_end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
        content = text[content_start:content_end].strip()
        sections.append({"heading": heading, "content": content})

    return sections


def tokenize(text):
    return set(re.findall(r"[a-z0-9]+", text.lower()))


def score_section(section, query_tokens):
    heading_tokens = tokenize(section["heading"])
    body_tokens = tokenize(section["content"])
    if not heading_tokens and not body_tokens:
        return 0.0

    heading_overlap = len(heading_tokens & query_tokens)
    body_overlap = len(body_tokens & query_tokens)

    # Weight heading matches higher than body matches.
    score = (3.0 * heading_overlap) + (1.0 * body_overlap)
    if query_tokens and query_tokens.issubset(heading_tokens):
        score += 8.0

    # Small length-normalization to avoid huge sections always winning.
    section_size = max(1, len(body_tokens))
    return score / (1 + (section_size / 120))


def build_section_index():
    index = []
    if not os.path.exists(PDF_FOLDER):
        return index

    for file in os.listdir(PDF_FOLDER):
        if not file.endswith(".pdf"):
            continue

        path = os.path.join(PDF_FOLDER, file)
        reader = PdfReader(path)

        for page_num, page in enumerate(reader.pages):
            raw_text = page.extract_text()
            if not raw_text:
                continue

            text = raw_text
            sections = split_sections(text)

            for section in sections:
                content = section["content"].strip()
                if not content:
                    continue
                index.append({
                    "file": file,
                    "page": page_num + 1,
                    "heading": clean_text(section["heading"]),
                    "content": clean_text(content),
                })

    return index


# -------------------------------
# MAIN SEARCH FUNCTION
# -------------------------------
def search_pdfs(query: str):
    if not os.path.exists(PDF_FOLDER):
        return [{"error": "PDF folder not found"}]

    query_tokens = set(extract_keywords(query))
    if not query_tokens:
        return [{"message": "Please provide a more specific report query."}]

    section_index = build_section_index()
    if not section_index:
        return [{"message": "No readable sections found in PDF reports."}]

    scored_sections = []
    for section in section_index:
        score = score_section(section, query_tokens)
        if score > 0:
            scored_sections.append((score, section))

    if not scored_sections:
        return [{"message": "No relevant info found"}]

    scored_sections.sort(key=lambda item: item[0], reverse=True)
    _, best = scored_sections[0]

    return [{
        "file": best["file"],
        "page": best["page"],
        "content": f"{best['heading']} {best['content']}".strip()
    }]