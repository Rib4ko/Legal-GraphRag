"""
Convert HTML tables (from PPStructure / SLANet) into Markdown tables,
with optional RTL text correction for Arabic cell contents.
"""
from bs4 import BeautifulSoup
from .rtl_utils import fix_arabic_line


def html_to_markdown_table(html: str, apply_rtl: bool = False) -> str:
    """
    Convert an HTML ``<table>`` element into a GitHub-Flavoured Markdown
    table.  If *apply_rtl* is True, every cell's text is passed through
    ``fix_arabic_line`` to correct PaddleOCR's visual-order output.
    """
    if not html:
        return ""

    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table")
    if not table:
        return ""

    rows = table.find_all("tr")
    if not rows:
        return ""

    md_rows: list[str] = []

    for i, row in enumerate(rows):
        cells = row.find_all(["td", "th"])
        cell_texts = []
        for cell in cells:
            txt = cell.get_text(strip=True).replace("|", "\\|")
            if apply_rtl:
                txt = fix_arabic_line(txt)
            cell_texts.append(txt)

        md_rows.append("| " + " | ".join(cell_texts) + " |")

        # Separator after the first row (treated as header)
        if i == 0:
            md_rows.append("| " + " | ".join(["---"] * len(cell_texts)) + " |")

    return "\n".join(md_rows)
