"""
RAG Engine Module
Main interface for the Retrieval Augmented Generation system.
Combines the chunker, retriever, and generator into a single pipeline
that the Flask backend can call with a simple ask() method.
"""

import os

from .chunker import DocumentChunker
from .retriever import DocumentRetriever
from .generator import AnswerGenerator


class RAGEngine:
    """
    Main RAG (Retrieval Augmented Generation) engine.

    This is the single entry point for the Flask backend.
    It loads the knowledge base, indexes documents, and answers questions.

    Usage:
        engine = RAGEngine()
        result = engine.ask("Which area in Mumbai is best for investment?")
        print(result['answer'])
    """

    def __init__(self, knowledge_dir=None):
        """
        Initialize the RAG Engine.

        Steps:
        1. Auto-detect the knowledge_base directory (relative to this file)
        2. Initialize the chunker, retriever, and generator
        3. Load and index all knowledge base documents

        Args:
            knowledge_dir (str, optional): Path to the knowledge base directory.
                If None, auto-detects using this file's location.
        """
        # Auto-detect knowledge_base directory relative to this file
        if knowledge_dir is None:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            knowledge_dir = os.path.join(current_dir, 'knowledge_base')

        self.knowledge_dir = knowledge_dir

        # Initialize pipeline components
        self.chunker = DocumentChunker(chunk_size=500, overlap=100)
        self.retriever = DocumentRetriever()
        self.generator = AnswerGenerator()

        # Track loading state
        self._ready = False

        # Load and index knowledge base
        self._load_knowledge_base()

    def _load_knowledge_base(self):
        """
        Load and index all documents from the knowledge base directory.

        Reads all .txt files, chunks them, and builds the TF-IDF index.
        Handles missing directory gracefully with a warning.
        """
        # Check if knowledge base directory exists
        if not os.path.isdir(self.knowledge_dir):
            print(f"Warning: Knowledge base directory '{self.knowledge_dir}' not found.")
            print("The RAG engine will not be able to answer questions.")
            return

        print(f"Loading knowledge base from: {self.knowledge_dir}")

        # Step 1: Chunk all documents in the knowledge base
        chunks = self.chunker.chunk_directory(self.knowledge_dir)

        if not chunks:
            print("Warning: No chunks were created. Check knowledge base files.")
            return

        # Step 2: Index chunks with TF-IDF
        self.retriever.index_chunks(chunks)

        self._ready = True
        print(f"RAG Engine ready! {len(chunks)} chunks indexed from knowledge base.")

    def ask(self, question):
        """
        Answer a question using the RAG pipeline.

        Steps:
        1. Retrieve the most relevant chunks for the question
        2. Generate a formatted answer from those chunks

        Args:
            question (str): The user's question about real estate.

        Returns:
            dict: Response with keys:
                - 'answer' (str): The formatted answer text.
                - 'sources' (list[dict]): Source chunks used, each with:
                    - 'text' (str): Chunk text content.
                    - 'file' (str): Source file name.
                    - 'score' (float): Relevance score.
        """
        # Handle unready state
        if not self._ready:
            return {
                'answer': "The knowledge base is not loaded. Please check that the knowledge_base directory exists with .txt files.",
                'sources': []
            }

        # Handle empty questions
        if not question or not question.strip():
            return {
                'answer': "Please ask a question about real estate in Mumbai, Delhi, or Bangalore.",
                'sources': []
            }

        # Step 1: Retrieve relevant chunks
        retrieved_chunks = self.retriever.retrieve(question, top_k=5)

        # Step 2: Generate answer from retrieved chunks
        result = self.generator.generate(question, retrieved_chunks)

        # Step 3: Format sources for the response
        sources = [
            {
                'text': chunk['text'],
                'file': chunk['source_file'],
                'score': chunk['relevance_score']
            }
            for chunk in retrieved_chunks
        ]

        return {
            'answer': result['answer'],
            'sources': sources
        }

    def is_ready(self):
        """
        Check if the knowledge base is loaded and ready.

        Returns:
            bool: True if knowledge base is loaded and indexed.
        """
        return self._ready
