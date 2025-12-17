# full_spancat_training_with_validation.py
import os
import json
import random
import unicodedata
import spacy
from spacy.training import Example

# -----------------------------
# Config
# -----------------------------
BASE_DIR = r"C:\MinorProject\ResumeScreening\Resume\ResumesJsonAnnotated"
OUTPUT_DIR = os.path.join(os.getcwd(), "span_model")
SPANS_KEY = "sc"
EPOCHS = 30
SHUFFLE = True
DROP = 0.2

# -----------------------------
# Utility: normalize text
# -----------------------------
def normalize_text(text: str) -> str:
    # NFC normalization and unify newlines
    text = unicodedata.normalize("NFC", text)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return text

# -----------------------------
# Utility: attempt to fix a bad span (very conservative)
# -----------------------------
def attempt_fix_span(text: str, start: int, end: int, max_expand=50):
    """
    Try to adjust start/end slightly if they are out of bounds or point to whitespace.
    Returns (new_start, new_end) or None if can't fix.
    """
    L = len(text)
    # clip to bounds
    start = max(0, start)
    end = min(L, end)
    if start < end and text[start:end].strip():
        return start, end

    # Try small expansions outward up to max_expand chars
    for expand in (1,2,3,5,10,20,50):
        s = max(0, start - expand)
        e = min(L, end + expand)
        if s < e and text[s:e].strip():
            return s, e

    return None

# -----------------------------
# Load JSON files from folder
# -----------------------------
def load_json_folder(folder):
    items = []
    for fn in sorted(os.listdir(folder)):
        if not fn.lower().endswith(".json"):
            continue
        path = os.path.join(folder, fn)
        try:
            with open(path, "r", encoding="utf-8") as f:
                obj = json.load(f)
                obj["_source_file"] = fn  # keep track for debugging
                items.append(obj)
        except Exception as e:
            print(f"Failed to read {fn}: {e}")
    return items

# -----------------------------
# Build TRAIN_DATA with validation + safe fixes
# -----------------------------
def build_train_data(items):
    train = []
    skipped_spans = []
    fixed_spans_count = 0
    total_spans = 0

    for item in items:
        raw_text = item.get("text", "")
        text = normalize_text(raw_text)
        raw_spans = item.get("spans", item.get("annotations", []))
        spans_list = []

        for raw in raw_spans:
            total_spans += 1
            # Expect raw like [start, end, label] or (start,end,label)
            try:
                start = int(raw[0])
                end = int(raw[1])
                label = raw[2]
            except Exception as e:
                skipped_spans.append((item.get("_source_file"), raw, "bad-format"))
                continue

            # quick bounds check
            if start < 0 or end > len(text) or start >= end:
                fixed = attempt_fix_span(text, start, end)
                if fixed:
                    start, end = fixed
                    fixed_spans_count += 1
                else:
                    skipped_spans.append((item.get("_source_file"), (start,end,label), "out-of-bounds"))
                    continue

            span_text = text[start:end]
            if not span_text.strip():
                # whitespace-only span: attempt fix
                fixed = attempt_fix_span(text, start, end)
                if fixed:
                    start, end = fixed
                    fixed_spans_count += 1
                    span_text = text[start:end]
                else:
                    skipped_spans.append((item.get("_source_file"), (start,end,label), "empty-or-whitespace"))
                    continue

            # final sanity: ensure substring length reasonable
            if len(span_text) == 0:
                skipped_spans.append((item.get("_source_file"), (start,end,label), "zero-length"))
                continue

            spans_list.append((start, end, label))

        if spans_list:
            train.append((text, {"spans": {SPANS_KEY: spans_list}}))
        else:
            # If an example ended up with zero valid spans, we still may want it for negative examples.
            # SpaCy requires at least an empty list for the spans key if you want no positives.
            train.append((text, {"spans": {SPANS_KEY: []}}))

    stats = {
        "total_examples": len(items),
        "total_spans_found": total_spans,
        "fixed_spans": fixed_spans_count,
        "skipped_spans": len(skipped_spans),
        "skipped_details": skipped_spans[:50],  # sample
    }
    return train, stats

# -----------------------------
# Main: prepare, train, save
# -----------------------------
def main():
    print("Loading spaCy model...")
    try:
        nlp = spacy.load("en_core_web_sm")
    except Exception as e:
        print("Failed to load en_core_web_sm:", e)
        print("Falling back to blank English model (less pretrained features).")
        nlp = spacy.blank("en")

    # add spancat if missing
    if "spancat" not in nlp.pipe_names:
        spancat = nlp.add_pipe(
            "spancat",
            config={
                "spans_key": SPANS_KEY,
                "threshold": 0.5,
                "max_positive": 200,
                "suggester": {"@misc": "spacy.ngram_suggester.v1", "sizes": [1, 2, 3]},
            },
        )
    else:
        spancat = nlp.get_pipe("spancat")

    print("Loading JSON files from:", BASE_DIR)
    items = load_json_folder(BASE_DIR)
    if not items:
        print("No JSON files found in folder. Exiting.")
        return

    print("Validating and building TRAIN_DATA...")
    TRAIN_DATA, stats = build_train_data(items)
    print("TRAIN_DATA examples:", len(TRAIN_DATA))
    print("Span stats:", {k: stats[k] for k in ("total_spans_found", "fixed_spans", "skipped_spans")})

    # Add labels to spancat
    labels = set()
    for _, ann in TRAIN_DATA:
        for tup in ann["spans"][SPANS_KEY]:
            labels.add(tup[2])
    for label in labels:
        spancat.add_label(label)
    print("Labels:", labels)

    # Train spancat only
    other_pipes = [p for p in nlp.pipe_names if p != "spancat"]
    with nlp.disable_pipes(*other_pipes):
        # initialize weights if needed
        optimizer = nlp.initialize(lambda: TRAIN_DATA)

        for epoch in range(EPOCHS):
            if SHUFFLE:
                random.shuffle(TRAIN_DATA)
            losses = {}
            for text, annotations in TRAIN_DATA:
                doc = nlp.make_doc(text)
                example = Example.from_dict(doc, annotations)
                try:
                    nlp.update([example], sgd=optimizer, drop=DROP, losses=losses)
                except Exception as e:
                    # catch unexpected per-example errors and report
                    print("Update error for an example — skipping it. Error:", e)
            print(f"Epoch {epoch+1}/{EPOCHS} - Losses: {losses}")

    # Save model
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    nlp.to_disk(OUTPUT_DIR)
    print("Saved model to:", OUTPUT_DIR)

    # Quick tests
    print("\nQuick test on a synthetic sentence:")
    test_text = "David Lee worked as Backend Engineer using Python and Django at WebApps Co from 2018 to 2021."
    doc = nlp(test_text)
    if SPANS_KEY in doc.spans:
        for span in doc.spans[SPANS_KEY]:
            print("PRED:", span.text, span.label_)
    else:
        print("No spans predicted for test sentence.")

    # show one example from TRAIN_DATA and how the model labels it
    print("\nSample training example check (first 1):")
    sample_text, sample_ann = TRAIN_DATA[0]
    print("TEXT (truncated):", sample_text[:300].replace("\n", "\\n"))
    print("GOLD SPANS:", sample_ann["spans"][SPANS_KEY])
    doc2 = nlp(sample_text)
    print("PRED SPANS:")
    for span in doc2.spans.get(SPANS_KEY, []):
        print(span.start_char, span.end_char, span.text, span.label_)

    # Print a few skipped details if any
    if stats["skipped_spans"]:
        print("\nSample skipped span details (up to 50):")
        for s in stats["skipped_details"]:
            print(s)

if __name__ == "__main__":
    main()
