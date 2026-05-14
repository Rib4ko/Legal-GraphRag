"""
Spatial reconstruction for Arabic OCR output.

Takes raw EasyOCR word-level bounding boxes and reconstructs a
structured Markdown document with:
- Correct RTL word/line ordering
- Header detection (by font size)
- Table detection (by columnar alignment)
- Numbered list detection (by leading digits)
- Confidence flagging ([?] markers for human review)
"""
import re
from typing import List, Dict
from statistics import median

_ARABIC_RE = re.compile(r"[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]")
_CONFIDENCE_THRESHOLD = 0.75


def is_arabic(text: str) -> bool:
    return bool(_ARABIC_RE.search(text))


def _parse_items(ocr_results) -> List[Dict]:
    """
    Parse raw EasyOCR results into items with coordinates + confidence.

    EasyOCR format: [(bbox, (text, conf)), ...]
    where bbox is [[x1,y1],[x2,y2],[x3,y3],[x4,y4]]

    NOTE: EasyOCR returns text in correct logical Unicode order.
    No character reversal is needed.
    """
    items = []
    for bbox, (text, conf) in ocr_results:
        xs = [p[0] for p in bbox]
        ys = [p[1] for p in bbox]
        items.append({
            "text": text,  # Already in correct logical order
            "conf": conf,
            "cx": sum(xs) / 4,
            "cy": sum(ys) / 4,
            "x_min": min(xs),
            "x_max": max(xs),
            "y_min": min(ys),
            "y_max": max(ys),
            "height": max(ys) - min(ys),
            "width": max(xs) - min(xs),
        })
    return items


def _group_into_lines(items: List[Dict], threshold: float = None) -> List[List[Dict]]:
    """Group items into visual lines based on Y-coordinate proximity."""
    if not items:
        return []
    if threshold is None:
        heights = [it["height"] for it in items if it["height"] > 0]
        threshold = median(heights) * 0.6 if heights else 10

    items_sorted = sorted(items, key=lambda i: i["cy"])
    lines = []
    current = [items_sorted[0]]
    for it in items_sorted[1:]:
        if abs(it["cy"] - current[0]["cy"]) <= threshold:
            current.append(it)
        else:
            lines.append(current)
            current = [it]
    lines.append(current)
    return lines


def _sort_line_rtl(line: List[Dict]) -> List[Dict]:
    """Sort words within a line from right to left (descending X)."""
    return sorted(line, key=lambda i: i["cx"], reverse=True)


def _flag_confidence(text: str, conf: float) -> str:
    """Mark low-confidence words with [?] for human review."""
    if conf < _CONFIDENCE_THRESHOLD and text.strip():
        return f"[?]{text}[?]"
    return text


def _line_text_with_confidence(line: List[Dict]) -> str:
    """Join line items, flagging low-confidence words."""
    parts = []
    for it in line:
        parts.append(_flag_confidence(it["text"], it["conf"]))
    return " ".join(parts)


def _is_number_token(text: str) -> bool:
    """Check if text is a number-like token (e.g. %5, 15%, .20)."""
    clean = text.strip().replace(" ", "")
    return bool(re.match(r"^[%٪.]?\s*\d+\.?\d*\s*[%٪.]?$", clean))


def _detect_numbered_list_start(line: List[Dict]) -> str:
    """
    Check if a line starts with a number (like .1 or 1. or ١.).
    Returns the number string if found, else empty string.
    """
    if not line:
        return ""
    # In Arabic RTL, the number is at the RIGHT side of the line (highest X)
    rightmost = max(line, key=lambda i: i["cx"])
    text = rightmost["text"].strip()
    # Match patterns like .1, 1., .2, ب, أ, ج
    if re.match(r"^\.?\d+\.?$", text) and len(text) <= 3:
        return text.strip(".")
    # Match Arabic letter markers (أ, ب, ج)
    if re.match(r"^[أبجدهوز]$", text):
        return text
    return ""


def _detect_table_block(lines: List[List[Dict]], start_idx: int,
                        page_width: float) -> List[int]:
    """
    Starting from start_idx, find consecutive lines that form a table.
    Table heuristic: lines where items are distributed across distinct
    X-position clusters (columns).
    """
    table_indices = []
    for i in range(start_idx, len(lines)):
        line = lines[i]
        if len(line) < 2:
            continue
        texts = [it["text"] for it in line]
        has_number = any(_is_number_token(t) for t in texts)
        has_arabic = any(is_arabic(t) for t in texts)
        # Check if items are spread across the line (not all bunched together)
        x_positions = sorted([it["cx"] for it in line])
        x_spread = x_positions[-1] - x_positions[0]
        is_spread = x_spread > page_width * 0.3

        if has_number and has_arabic and is_spread and 2 <= len(line) <= 10:
            table_indices.append(i)
        elif table_indices:
            # Check if this could be the last row (like row 6 with long text)
            if has_number and has_arabic and len(table_indices) >= 2:
                table_indices.append(i)
            break  # table ended

    return table_indices if len(table_indices) >= 3 else []


def _build_table_markdown(table_lines: List[List[Dict]]) -> str:
    """Convert table lines into a Markdown table."""
    rows = []
    for line in table_lines:
        sorted_line = _sort_line_rtl(line)
        # Classify items by X position into columns
        # Rightmost = row number, middle = content, leftmost = percentage
        items_by_x = sorted(sorted_line, key=lambda i: i["cx"])
        # Leftmost item (in LTR space) = percentage (left column in original)
        # Rightmost items = row number + content
        pct_item = items_by_x[0]  # leftmost = percentage column
        row_num_item = items_by_x[-1]  # rightmost = row number

        pct = _flag_confidence(pct_item["text"], pct_item["conf"])
        row_num = ""
        if _is_number_token(row_num_item["text"]):
            row_num = row_num_item["text"].strip(".")
            content_items = items_by_x[1:-1]
        else:
            content_items = items_by_x[1:]

        content_parts = [_flag_confidence(it["text"], it["conf"]) for it in content_items]
        # Content is Arabic, so reverse the order (we sorted by X ascending)
        content_parts.reverse()
        content = " ".join(content_parts)

        rows.append(f"| {row_num} | {content} | {pct} |")

    if not rows:
        return ""
    header = "| # | البند | النسبة |"
    sep = "| --- | --- | --- |"
    return "\n".join([header, sep] + rows)


def reconstruct_arabic_markdown(ocr_results, page_num: int = 1) -> str:
    """
    Main entry point: raw EasyOCR results → structured Markdown.
    """
    if not ocr_results:
        return ""

    items = _parse_items(ocr_results)
    if not items:
        return ""

    lines = _group_into_lines(items)
    for i in range(len(lines)):
        lines[i] = _sort_line_rtl(lines[i])

    # Stats for structure detection
    all_heights = [it["height"] for line in lines for it in line]
    med_height = median(all_heights) if all_heights else 20
    page_width = max(it["x_max"] for it in items) - min(it["x_min"] for it in items)

    # Detect table block
    table_indices = set()
    for start in range(len(lines)):
        if start not in table_indices:
            found = _detect_table_block(lines, start, page_width)
            if found:
                table_indices.update(found)
                break  # only one table expected per page for now

    # Build markdown
    sections = [f"## Page {page_num}"]
    table_buffer = []
    i = 0
    while i < len(lines):
        line = lines[i]
        line_text = _line_text_with_confidence(line)
        max_h = max(it["height"] for it in line)

        # --- Table ---
        if i in table_indices:
            table_buffer.append(line)
            i += 1
            continue
        elif table_buffer:
            sections.append(_build_table_markdown(table_buffer))
            table_buffer = []

        # --- Header (large font) ---
        if max_h > med_height * 1.5 and len(line) <= 6:
            level = "#" if max_h > med_height * 2.0 else "###"
            sections.append(f"{level} {line_text}")
            i += 1
            continue

        # --- Numbered list ---
        list_num = _detect_numbered_list_start(line)
        if list_num:
            # Remove the number token from the line text
            remaining = [it for it in line
                         if it["text"].strip(".") != list_num]
            remaining_text = " ".join(
                _flag_confidence(it["text"], it["conf"]) for it in remaining
            )
            # Check if next lines are continuation (no new number)
            continuation = []
            j = i + 1
            while j < len(lines) and j not in table_indices:
                next_num = _detect_numbered_list_start(lines[j])
                next_h = max(it["height"] for it in lines[j])
                if next_num or next_h > med_height * 1.5:
                    break
                continuation.append(
                    _line_text_with_confidence(lines[j])
                )
                j += 1
            full_text = remaining_text
            if continuation:
                full_text += " " + " ".join(continuation)
            sections.append(f"{list_num}. {full_text}")
            i = j
            continue

        # --- Regular text ---
        if line_text.strip():
            sections.append(line_text)
        i += 1

    # Flush remaining table
    if table_buffer:
        sections.append(_build_table_markdown(table_buffer))

    return "\n\n".join(sections)
