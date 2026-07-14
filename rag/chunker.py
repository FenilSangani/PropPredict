"""
Document Chunker Module
Splits text documents into overlapping chunks for RAG retrieval.
Uses character-based chunking with configurable size and overlap.
"""

import os


class DocumentChunker:
    """Splits text documents into overlapping chunks for indexing and retrieval."""

    def __init__(self, chunk_size=300, overlap=50):
        """
        Initialize the DocumentChunker.

        Args:
            chunk_size (int): Target size of each chunk in characters. Default 300.
            overlap (int): Number of overlapping characters between consecutive chunks. Default 50.
        """
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk_text(self, text):
        """
        Split text into overlapping chunks.

        Each chunk is approximately chunk_size characters long, with overlap
        characters shared between consecutive chunks. This overlap ensures
        that important information at chunk boundaries is not lost.

        Args:
            text (str): The text to split into chunks.

        Returns:
            list[str]: List of text chunks.
        """
        # Return empty list for empty or whitespace-only text
        if not text or not text.strip():
            return []

        chunks = []
        start = 0
        text_length = len(text)

        while start < text_length:
            # Calculate end position for this chunk
            end = start + self.chunk_size

            # If we've reached the end of the text, take whatever is left
            if end >= text_length:
                chunk = text[start:].strip()
                if chunk:  # Only add non-empty chunks
                    chunks.append(chunk)
                break

            # Try to break at a sentence boundary (period, newline) for cleaner chunks
            # Look backwards from the end position to find a natural break point
            break_point = end
            for i in range(end, max(start + self.chunk_size // 2, start), -1):
                if text[i] in '.!\n':
                    break_point = i + 1
                    break

            chunk = text[start:break_point].strip()
            if chunk:  # Only add non-empty chunks
                chunks.append(chunk)

            # Move start forward by (chunk_size - overlap) to create overlap
            start = break_point - self.overlap

            # Safety: ensure we always move forward to avoid infinite loops
            if start <= (break_point - self.chunk_size):
                start = break_point

        return chunks

    def chunk_file(self, filepath):
        """
        Read a file and split it into chunks with metadata.

        Args:
            filepath (str): Path to the text file to chunk.

        Returns:
            list[dict]: List of dicts with keys:
                - 'text' (str): The chunk text content.
                - 'source_file' (str): Name of the source file.
        """
        # Read the file content
        with open(filepath, 'r', encoding='utf-8') as f:
            text = f.read()

        # Get just the filename for source attribution
        source_name = os.path.basename(filepath)

        # Chunk the text and attach metadata
        chunks = self.chunk_text(text)
        return [
            {'text': chunk, 'source_file': source_name}
            for chunk in chunks
        ]

    def chunk_directory(self, dir_path):
        """
        Chunk all .txt files in a directory.

        Scans the directory for .txt files, reads and chunks each one,
        and returns all chunks with their source file metadata.

        Args:
            dir_path (str): Path to the directory containing .txt files.

        Returns:
            list[dict]: Combined list of chunk dicts from all files.
                Each dict has keys: 'text', 'source_file'.
        """
        all_chunks = []

        # Check if directory exists
        if not os.path.isdir(dir_path):
            print(f"Warning: Directory '{dir_path}' not found.")
            return all_chunks

        # Process each .txt file in the directory
        for filename in sorted(os.listdir(dir_path)):
            if filename.endswith('.txt'):
                filepath = os.path.join(dir_path, filename)
                file_chunks = self.chunk_file(filepath)
                all_chunks.extend(file_chunks)
                print(f"  Chunked '{filename}' -> {len(file_chunks)} chunks")

        print(f"Total chunks created: {len(all_chunks)}")
        return all_chunks
