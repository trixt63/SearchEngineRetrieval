import fitz
import json

from database.search_engine import SearchEngine
from utils.logger_utils import get_logger

TITLE_AND_TREE_CONTENTS = 25

NEW_PARAGRAPH_THRESHOLD = 28

SECTION_FONTSIZE = 20
SUBSECTION_FONTSIZE = 18
SUBSUBSECTION_FONTSIZE = 16

logger = get_logger("Ingest book")


def get_paragraphs(pdf_path: str):
    search_engine = SearchEngine()
    pdf = fitz.open(pdf_path)

    sections = []
    paragraphs = []
    for _page_nth in range(TITLE_AND_TREE_CONTENTS, len(pdf)):
        page = pdf.load_page(_page_nth)
        blocks = page.get_text("dict")["blocks"]
        line_counter = 0
        page_paragraphs = []
        _is_new_paragraph = True

        previous_y = None
        for block in blocks:
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        font_size = span["size"]
                        text = span["text"].strip()
                        page_number = _page_nth - TITLE_AND_TREE_CONTENTS + 1

                        # Page header/footer
                        if font_size == 8:
                            continue

                        line_counter += 1
                        current_y = line["bbox"][1]
                        # Section
                        if font_size == SECTION_FONTSIZE:
                            sections.append({
                                "page_number": page_number,
                                "line_number": line_counter,
                                "title": text,
                                "subsections": []
                            })
                            _is_new_paragraph = True

                        # Subsection
                        elif font_size == SUBSECTION_FONTSIZE:
                            sections[-1]["subsections"].append({
                                "page_number": page_number,
                                "line_number": line_counter,
                                "title": text,
                                "subsubsections": []
                            })
                            _is_new_paragraph = True

                        # Sub-subsection
                        elif font_size == SUBSUBSECTION_FONTSIZE:
                            sections[-1]["subsections"][-1]["subsubsections"].append({
                                "page_number": page_number,
                                "line_number": line_counter,
                                "title": text,
                            })
                            _is_new_paragraph = True

                        # paragraph
                        else:
                            if previous_y is not None and abs(current_y - previous_y) > NEW_PARAGRAPH_THRESHOLD:
                                _is_new_paragraph = True
                            if not _is_new_paragraph:
                                page_paragraphs[-1]["text"] += text
                                page_paragraphs[-1]["lines"][1] = line_counter
                                _is_new_paragraph = False
                            else:
                                _new_paragraph = {
                                    "page_number": page_number,
                                    "lines": [line_counter, line_counter],
                                    "text": text,
                                    "section": sections[-1]["title"],
                                }
                                if sections[-1]["subsections"]:
                                    _new_paragraph["subsection"] = sections[-1]["subsections"][-1]["title"]
                                    if sections[-1]["subsections"][-1]["subsubsections"]:
                                        _subsubsections = sections[-1]["subsections"][-1]["subsubsections"][-1]['title']
                                        _new_paragraph["subsubsection"] = _subsubsections

                                page_paragraphs.append(_new_paragraph)
                                _is_new_paragraph = False

                        previous_y = current_y

        # Export to Elastic search
        ingest(data=page_paragraphs, search_engine=search_engine)
        paragraphs.extend(page_paragraphs)

        # progress
        if not _page_nth % 100:
            logger.info(f"To page {_page_nth} / {len(pdf)}. Progress: {_page_nth / len(pdf) * 100:.2f}%")

    pdf.close()
    return paragraphs


def ingest(data: list[dict], search_engine: SearchEngine):
    dict_with_id = {
        f"{doc['page_number']}_{doc['lines'][0]}_{doc['lines'][0]}": doc
        for doc in data
    }
    search_engine.import_bulk(documents=dict_with_id)


if __name__ == '__main__':
    pdf_path = 'data/s3-userguide.pdf'
    paragraphs = get_paragraphs(pdf_path)
    with open('data/paragraphs.json', 'w') as f:
        json.dump(paragraphs, f, indent=2)
