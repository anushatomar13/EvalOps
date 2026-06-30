import csv
import io
from typing import List, Tuple

# Flexible column matching: many task types name their columns differently,
# but they all map to a "question" and an "expected answer".
QUESTION_ALIASES = ["question", "prompt", "input", "query", "instruction"]
ANSWER_ALIASES = [
    "ground truth",
    "ground_truth",
    "expected",
    "expected sql",
    "expected_sql",
    "answer",
    "unit tests",
    "unit_tests",
    "correct documents",
    "correct_documents",
    "reference",
]
CONTEXT_ALIASES = ["context", "documents", "docs", "retrieved", "source"]


def _pick(header_map: dict, aliases: List[str]) -> str | None:
    for alias in aliases:
        if alias in header_map:
            return header_map[alias]
    return None


def parse_csv(content: bytes) -> Tuple[List[dict], List[str]]:
    """Parse CSV bytes into a list of {question, ground_truth, context} rows.

    Returns (rows, warnings). Column names are matched case-insensitively
    against known aliases; the first column is used as the question if no
    known alias is present.
    """
    text = content.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text))
    if not reader.fieldnames:
        raise ValueError("CSV has no header row")

    # Map lowercased header -> original header.
    header_map = {h.strip().lower(): h for h in reader.fieldnames}
    q_col = _pick(header_map, QUESTION_ALIASES) or reader.fieldnames[0]
    a_col = _pick(header_map, ANSWER_ALIASES)
    c_col = _pick(header_map, CONTEXT_ALIASES)

    warnings: List[str] = []
    if a_col is None:
        warnings.append(
            "No ground-truth column detected; evaluation will run without reference answers."
        )

    rows: List[dict] = []
    for raw in reader:
        question = (raw.get(q_col) or "").strip()
        if not question:
            continue
        rows.append(
            {
                "question": question,
                "ground_truth": (raw.get(a_col) or "").strip() if a_col else "",
                "context": (raw.get(c_col) or "").strip() if c_col else "",
            }
        )
    if not rows:
        raise ValueError("CSV contained no data rows")
    return rows, warnings
