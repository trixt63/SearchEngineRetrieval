import fitz
from PyPDF2 import PdfReader
import logging
import json

TITLE_AND_TREE_CONTENTS = 25

SECTION_FONTSIZE = 20
SUBSECTION_FONTSIZE = 18
SUBSUBSECTION_FONTSIZE = 16


def get_paragraphs():
    pdf_path = '../data/s3-userguide.pdf'
    pdf = fitz.open(pdf_path)

    sections = []
    paragraphs = []
    for _page_nth in range(TITLE_AND_TREE_CONTENTS, len(pdf)):
        page = pdf.load_page(_page_nth)
        blocks = page.get_text("dict")["blocks"]
        line_counter = 0
        page_paragraphs = []
        _is_new_paragraph = True

        previous_y = None  # To track the Y-coordinate of the last line
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

                        line_counter += 1  # Increment for each new line in the page
                        current_y = line["bbox"][1]  # Top Y-coordinate of the line
                        # Section
                        if font_size == SECTION_FONTSIZE:
                            sections.append({
                                "page_number": page_number,
                                "line_number": line_counter,  # Track exact line number
                                "title": text,
                                "subsections": []
                            })
                            _is_new_paragraph = True

                        # Subsection
                        elif font_size == SUBSECTION_FONTSIZE:
                            sections[-1]["subsections"].append({
                                "page_number": page_number,
                                "line_number": line_counter,  # Track exact line number
                                "title": text,
                                "subsubsections": []
                            })
                            _is_new_paragraph = True

                        # Sub-subsection
                        elif font_size == SUBSUBSECTION_FONTSIZE:
                            # subsubsection_title = subsection_title + " > " + text
                            sections[-1]["subsections"][-1]["subsubsections"].append({
                                "page_number": page_number,
                                "line_number": line_counter,  # Track exact line number
                                "title": text,
                            })
                            _is_new_paragraph = True

                        # paragraph
                        else:
                            if previous_y is not None and abs(current_y - previous_y) > 28.0:  # Example threshold
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

        paragraphs.append(page_paragraphs)

    pdf.close()
    logging.info(f"number of sections: {len(sections)}")
    return paragraphs


if __name__ == '__main__':
    paragraphs = get_paragraphs()
    with open('../data/paragraphs.json', 'w') as f:
        json.dump(paragraphs, f, indent=2)
