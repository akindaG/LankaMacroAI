"""Stage a local PDF for review; never publish extracted numbers automatically."""

import argparse
import hashlib
import json
import shutil
from pathlib import Path

from pypdf import PdfReader

from .database import ROOT


def stage(file: Path, title: str, publisher: str, source_url: str):
    if not file.is_file() or file.suffix.lower() != ".pdf":
        raise ValueError("Provide a local PDF file")
    if file.stat().st_size > 30 * 1024 * 1024:
        raise ValueError("PDF exceeds the 30 MiB staging limit")
    digest = hashlib.sha256(file.read_bytes()).hexdigest()
    destination = ROOT / "var/staging" / digest
    destination.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(file, destination / "original.pdf")
    pages = [
        {"page": i + 1, "text": page.extract_text() or ""}
        for i, page in enumerate(PdfReader(file).pages)
    ]
    record = {
        "sha256": digest,
        "title": title,
        "publisher": publisher,
        "source_url": source_url,
        "status": "needs_ocr_and_review"
        if not all(p["text"].strip() for p in pages)
        else "needs_review",
        "pages": pages,
    }
    (destination / "extraction.json").write_text(
        json.dumps(record, indent=2), encoding="utf-8"
    )
    return destination


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file", type=Path)
    parser.add_argument("--title", required=True)
    parser.add_argument("--publisher", required=True)
    parser.add_argument("--source-url", required=True)
    args = parser.parse_args()
    print(stage(args.file, args.title, args.publisher, args.source_url))


if __name__ == "__main__":
    main()
