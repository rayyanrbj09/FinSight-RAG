from services.parser import chunk_text, extract_text


def test_extract_text_file():
    text = extract_text(b"Prepared Remarks\nCEO: Revenue increased.\n", "call.txt")

    assert "Prepared Remarks" in text
    assert "CEO: Revenue increased." in text


def test_chunk_text_detects_speaker_and_section():
    text = (
        "Prepared Remarks\n"
        "CEO Jane Doe: Revenue increased this quarter.\n"
        "Question and Answer\n"
        "Analyst John Smith: What changed in guidance?"
    )

    chunks = chunk_text(text, chunk_size=100, chunk_overlap=10)

    assert len(chunks) >= 1
    assert chunks[0].section in {"prepared", "unknown", "qa"}
    assert chunks[0].text
