"""
Document Retriever Module
Uses TF-IDF vectorization and cosine similarity to find relevant chunks.
Built on scikit-learn's TfidfVectorizer and cosine_similarity.
"""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class DocumentRetriever:
    """Retrieves the most relevant document chunks for a given query using TF-IDF."""

    def __init__(self):
        """
        Initialize the DocumentRetriever.

        Sets up the TF-IDF vectorizer with settings tuned for
        real estate document retrieval.
        """
        # Configure TF-IDF with reasonable defaults for document retrieval
        # - ngram_range=(1,2): captures single words and two-word phrases
        #   e.g., "bandra", "property price", "metro connectivity"
        # - stop_words='english': removes common words like "the", "is", "at"
        # - max_features=5000: limits vocabulary to top 5000 terms
        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            stop_words='english',
            max_features=5000
        )

        # Storage for indexed chunks and their TF-IDF matrix
        self.chunks = []         # List of chunk dicts
        self.tfidf_matrix = None  # TF-IDF matrix (num_chunks x num_features)
        self.is_indexed = False   # Flag to check if indexing is done

    def index_chunks(self, chunks):
        """
        Build a TF-IDF index from a list of document chunks.

        Takes the chunk texts, fits the TF-IDF vectorizer, and stores
        the resulting matrix for later similarity queries.

        Args:
            chunks (list[dict]): List of chunk dicts, each with at least a 'text' key.
        """
        if not chunks:
            print("Warning: No chunks provided for indexing.")
            return

        # Store chunks for later retrieval
        self.chunks = chunks

        # Extract text from each chunk for vectorization
        texts = [chunk['text'] for chunk in chunks]

        # Fit the vectorizer and transform texts into TF-IDF matrix
        # Shape: (num_chunks, num_features)
        self.tfidf_matrix = self.vectorizer.fit_transform(texts)
        self.is_indexed = True

        print(f"Indexed {len(chunks)} chunks with {self.tfidf_matrix.shape[1]} features")

    def retrieve(self, query, top_k=3):
        """
        Find the top_k most relevant chunks for a given query.

        Steps:
        1. Transform the query using the fitted TF-IDF vectorizer
        2. Calculate cosine similarity between query and all chunks
        3. Return top_k chunks sorted by relevance score (highest first)

        Args:
            query (str): The search query text.
            top_k (int): Number of top results to return. Default 3.

        Returns:
            list[dict]: Top matching chunks, each with keys:
                - 'text' (str): The chunk text content.
                - 'source_file' (str): Name of the source file.
                - 'relevance_score' (float): Cosine similarity score (0 to 1).
        """
        # Check if index is ready
        if not self.is_indexed:
            print("Warning: No documents indexed. Call index_chunks() first.")
            return []

        # Transform query using the same vectorizer (uses learned vocabulary)
        query_vector = self.vectorizer.transform([query])

        # Calculate cosine similarity between query and all chunks
        # Returns shape: (1, num_chunks)
        similarities = cosine_similarity(query_vector, self.tfidf_matrix)[0]

        # Get indices of top_k highest similarity scores
        # argsort returns ascending order, so we reverse and take top_k
        top_indices = similarities.argsort()[::-1][:top_k]

        # Build results list with chunk data and scores
        results = []
        for idx in top_indices:
            score = float(similarities[idx])
            # Only include results with non-zero relevance
            if score > 0:
                results.append({
                    'text': self.chunks[idx]['text'],
                    'source_file': self.chunks[idx]['source_file'],
                    'relevance_score': round(score, 4)
                })

        return results
