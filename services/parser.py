"""Transcript parsing and chunking services."""

from dataclasses import dataclass
from io import BytesIO
import re

from pypdf import PdfReader


@dataclass(frozen=True)
class TranscriptChunk:
    """A parsed chunk with earnings-call metadata."""

    text: str
    speaker: str | None
    role: str | None
    section: str


def extract_text(file_bytes: bytes, filename: str) -> str:
    """Extract normalized text from a PDF or text file."""
    extension = filename.lower().rsplit(".", 1)[-1] if "." in filename else ""

    if extension == "pdf":
        reader = PdfReader(BytesIO(file_bytes))
        pages = [page.extract_text() or "" for page in reader.pages]
        text = "\n".join(pages)
    elif extension in {"txt", "text"}:
        text = file_bytes.decode("utf-8-sig")
    else:
        raise ValueError("Unsupported file type")

    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _detect_section(text: str) -> str:
    heading = text.lower()
    if "question" in heading and "answer" in heading:
        return "qa"
    if re.search(r"\b(q\s*&?\s*a|qa|questions)\b", heading):
        return "qa"
    if "prepared remarks" in heading or "presentation" in heading:
        return "prepared"
    return "unknown"


def _detect_speaker(line: str) -> tuple[str | None, str | None]:
    match = re.match(r"^([^:\n]{2,100})\s*[:\-]\s*", line.strip())
    if not match:
        return None, None

    speaker = match.group(1).strip()
    upper = speaker.upper()

    role: str | None = None
    if "CEO" in upper or "CHIEF EXECUTIVE" in upper:
        role = "CEO"
    elif "CFO" in upper or "CHIEF FINANCIAL" in upper:
        role = "CFO"
    elif "ANALYST" in upper or "INVESTOR" in upper:
        role = "analyst"
    elif "OPERATOR" in upper or "MODERATOR" in upper:
        role = "operator"

    speaker = re.sub(r"\s*\(([^()]*)\)\s*$", "", speaker).strip()
    return speaker, role


def chunk_text(
    text: str,
    chunk_size: int = 500,
    chunk_overlap: int = 50,
) -> list[TranscriptChunk]:
    """Chunk text while retaining speaker and section metadata."""
    if chunk_size < 100 or chunk_overlap < 0 or chunk_overlap >= chunk_size:
        raise ValueError("Invalid chunk size or overlap")

    words = text.split()
    if not words:
        return []

    words_per_chunk = chunk_size
    step = max(1, words_per_chunk - chunk_overlap)
    chunks: list[TranscriptChunk] = []

    section = "unknown"
    speaker: str | None = None
    role: str | None = None

    for start in range(0, len(words), step):
        chunk_words = words[start:start + words_per_chunk]
        chunk_text = " ".join(chunk_words)

        for line in chunk_text.split("\n"):
            heading_section = _detect_section(line)
            if heading_section != "unknown":
                section = heading_section

            line_speaker, line_role = _detect_speaker(line)
            if line_speaker:
                speaker = line_speaker
                role = line_role

        chunks.append(
            TranscriptChunk(
                text=chunk_text,
                speaker=speaker,
                role=role,
                section=section,
            )
        )

    return chunks
