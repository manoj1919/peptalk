# tests/test_processing.py

import pytest
from src.peptalk.processing import chunk_text # Notice the 'src.' import

# A simple, small piece of text for our test
SAMPLE_TEXT = """
This is the first sentence. It forms the first paragraph.

This is the second paragraph. It has two sentences. This is the second sentence.

This is a very long third paragraph that is designed to be longer than
the chunk size, forcing the splitter to make a decision. We will set the
chunk size to be very small for this test to ensure that it actually
splits this paragraph into multiple pieces. This is the end of the long
paragraph.
"""

def test_chunk_text_simple():
    """Tests that the chunker splits text into multiple chunks."""
    chunks = chunk_text(SAMPLE_TEXT, chunk_size=50, chunk_overlap=10)
    assert len(chunks) > 1 

def test_chunk_text_size_and_overlap():
    """Tests that chunks respect the chunk_size (approximately)."""
    chunk_size = 50
    chunks = chunk_text(SAMPLE_TEXT, chunk_size=chunk_size, chunk_overlap=10)
    for chunk in chunks:
        assert len(chunk) <= chunk_size * 1.1 

def test_chunk_text_empty_input():
    """Tests that empty text returns an empty list."""
    chunks = chunk_text("", chunk_size=100, chunk_overlap=10)
    assert len(chunks) == 0

def test_chunk_text_overlap():
    """Tests that overlap is present."""
    test_text = "abcdefghijklmnopqrstuvwxyz" * 5
    chunks = chunk_text(test_text, chunk_size=26, chunk_overlap=5)
    
    overlap = chunks[0][-5:] 
    assert chunks[1].startswith(overlap)