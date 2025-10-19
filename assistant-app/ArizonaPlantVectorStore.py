from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

class ArizonaPlantVectorStore:
    def __init__(self, 
                 embedding_model_name='all-MiniLM-L6-v2',
                 collection_name='arizona_plants'):
        """
        Initialize the vector store
        
        Args:
            embedding_model_name: SentenceTransformer model name
            collection_name: Name for the Qdrant collection
        """
        self.collection_name = collection_name
        
        # Initialize embedding model
        print(f"Loading embedding model: {embedding_model_name}")
        self.embedding_model = SentenceTransformer(embedding_model_name)
        self.embedding_dim = self.embedding_model.get_sentence_embedding_dimension()
        print(f"✓ Model loaded (dimension: {self.embedding_dim})")
        
        # Initialize Qdrant client
        self.client = QdrantClient()
        print("✓ Qdrant client initialized")
    
    def search(self, query: str, limit: int = 5):
        """
        Search for relevant documents using pre-computed embeddings
        
        Args:
            query: Search query string
            limit: Number of results to return
            
        Returns:
            List of search results with metadata
        """
        print(f'Searching for: "{query}"')
        
        # Encode the query using SentenceTransformer
        query_embedding = self.embedding_model.encode(query)
        
        # Search in Qdrant using the embedding vector
        search_results = self.client.query_points(
            collection_name=self.collection_name,
            query=query_embedding.tolist(),  # Pass the vector directly, not wrapped in Document
            limit=limit,
            with_payload=True
        )

        # Format results
        results = []
        for point in search_results.points:  # Note: .points here
            result = {
                'id': point.payload.get('id', 'N/A'),
                'score': point.score,
                'title': point.payload.get('title', 'Untitled'),
                'content': point.payload.get('content', ''),
                'type': point.payload.get('type', ''),
                'source': point.payload.get('source', ''),
                'metadata': point.payload.get('metadata', {})
            }
            results.append(result)
        
        print(f"✓ Found {len(results)} results")
        return results
