from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
from typing import List, Dict
from pathlib import Path

import os
import json


class ArizonaPlantVectorStore:
    def __init__(self, 
                 embedding_model_name='all-MiniLM-L6-v2',
                 collection_name='arizona_plants',
                 qdrant_url='http://localhost:6333'):
        """
        Initialize the vector store
        
        Args:
            embedding_model_name: HuggingFace model for embeddings
                - 'all-MiniLM-L6-v2': Fast, 384 dimensions (recommended)
                - 'all-mpnet-base-v2': Better quality, 768 dimensions
                - 'multi-qa-MiniLM-L6-cos-v1': Optimized for Q&A
            collection_name: Name for the Qdrant collection
        """
        print("="*60)
        print("Arizona Desert Plants RAG - Vector Store Setup")
        print("="*60)
        
        self.collection_name = collection_name
        self.qdrant_url = qdrant_url
        
        # Initialize embedding model
        print(f"\n1. Loading embedding model: {embedding_model_name}")
        self.embedding_model = SentenceTransformer(embedding_model_name)
        self.embedding_dim = self.embedding_model.get_sentence_embedding_dimension()
        print(f"   ✓ Model loaded (dimension: {self.embedding_dim})")
        
        # Initialize Qdrant client
        print("\n2. Initializing Qdrant client")
        self.client = QdrantClient(url=self.qdrant_url)
        print("   ✓ Client initialized")
        
    def load_dataset(self, dataset_path: str) -> List[Dict]:
        """Load the unified dataset"""
        print(f"\n3. Loading dataset from: {dataset_path}")
        
        path = Path(dataset_path)
        
        if not path.exists():
            raise FileNotFoundError(f"Dataset not found: {dataset_path}")
        
        # Handle different file formats
        if path.suffix == '.json':
            with open(path, 'r', encoding='utf-8') as f:
                documents = json.load(f)
        elif path.suffix == '.jsonl':
            documents = []
            with open(path, 'r', encoding='utf-8') as f:
                for line in f:
                    documents.append(json.loads(line))
        else:
            raise ValueError(f"Unsupported file format: {path.suffix}")
        
        print(f"   ✓ Loaded {len(documents)} documents")
        return documents
    
    def create_collection(self):
        """Create Qdrant collection"""
        print(f"\n4. Creating collection: {self.collection_name}")
        
        # Delete if exists (for fresh start)
        try:
            self.client.delete_collection(self.collection_name)
            print("   - Deleted existing collection")
        except:
            pass
        
        # Create collection
        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(
                size=self.embedding_dim,
                distance=Distance.COSINE  # Cosine similarity for semantic search
            )
        )
        print(f"   ✓ Collection created (vector size: {self.embedding_dim})")
    
    def prepare_text_for_embedding(self, document: Dict) -> str:
        """
        Prepare document text for embedding
        Combine title and content for better semantic representation
        """
        title = document.get('title', '')
        content = document.get('content', '')
        
        # Combine title and content (title gets more weight by being first)
        text = f"{title}\n\n{content}"
        
        # Limit to reasonable length (most embedding models have token limits)
        max_chars = 5000  # Adjust based on your model
        if len(text) > max_chars:
            text = text[:max_chars]
        
        return text
    
    def create_embeddings(self, documents: List[Dict], batch_size: int = 32) -> List[Dict]:
        """
        Create embeddings for all documents
        
        Args:
            documents: List of document dicts
            batch_size: Number of documents to process at once
            
        Returns:
            List of dicts with documents and their embeddings
        """
        print(f"\n5. Creating embeddings (batch size: {batch_size})")
        
        # Prepare texts
        texts = [self.prepare_text_for_embedding(doc) for doc in documents]
        
        # Create embeddings in batches
        all_embeddings = []
        
        print("   Processing batches...")
        for i in tqdm(range(0, len(texts), batch_size), desc="   Embedding"):
            batch_texts = texts[i:i + batch_size]
            batch_embeddings = self.embedding_model.encode(
                batch_texts,
                show_progress_bar=False,
                convert_to_numpy=True
            )
            all_embeddings.extend(batch_embeddings)
        
        print(f"   ✓ Created {len(all_embeddings)} embeddings")
        
        # Combine documents with embeddings
        documents_with_embeddings = [
            {
                'document': doc,
                'embedding': embedding,
                'text': text
            }
            for doc, embedding, text in zip(documents, all_embeddings, texts)
        ]
        
        return documents_with_embeddings
    
    def upload_to_qdrant(self, documents_with_embeddings: List[Dict]):
        """Upload documents and embeddings to Qdrant"""
        print(f"\n6. Uploading to Qdrant")
        
        points = []
        for idx, item in enumerate(documents_with_embeddings):
            doc = item['document']
            embedding = item['embedding']
            
            # Create point with embedding and metadata
            point = PointStruct(
                id=idx,
                vector=embedding.tolist(),
                payload={
                    'id': doc.get('id'),
                    'type': doc.get('type'),
                    'source': doc.get('source'),
                    'title': doc.get('title'),
                    'content': doc.get('content'),
                    'metadata': doc.get('metadata', {})
                }
            )
            points.append(point)
        
        # Upload in batches
        batch_size = 100
        print(f"   Uploading in batches of {batch_size}...")
        
        for i in tqdm(range(0, len(points), batch_size), desc="   Uploading"):
            batch = points[i:i + batch_size]
            self.client.upsert(
                collection_name=self.collection_name,
                points=batch
            )
        
        print(f"   ✓ Uploaded {len(points)} documents")
    
    def build_index(self, dataset_path: str):
        """Complete pipeline: load data, create embeddings, upload to Qdrant"""
        # Load dataset
        documents = self.load_dataset(dataset_path)
        
        # Create collection
        self.create_collection()
        
        # Create embeddings
        documents_with_embeddings = self.create_embeddings(documents)
        
        # Upload to Qdrant
        self.upload_to_qdrant(documents_with_embeddings)
        
        # Verify
        collection_info = self.client.get_collection(self.collection_name)
        print(f"\n{'='*60}")
        print("✓ Index built successfully!")
        print(f"{'='*60}")
        print(f"Collection: {self.collection_name}")
        print(f"Total vectors: {collection_info.points_count}")
        print(f"Vector dimension: {self.embedding_dim}")
        
    def search(self, query: str, limit: int = 5) -> List[Dict]:
        """
        Search for relevant documents
        
        Args:
            query: Search query
            limit: Number of results to return
            
        Returns:
            List of matching documents with scores
        """
        # Embed the query
        query_embedding = self.embedding_model.encode(query)
        
        # Search in Qdrant
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding.tolist(),
            limit=limit
        )
        
        # Format results
        formatted_results = []
        for result in results:
            formatted_results.append({
                'score': result.score,
                'id': result.payload.get('id'),
                'title': result.payload.get('title'),
                'type': result.payload.get('type'),
                'source': result.payload.get('source'),
                'content': result.payload.get('content')[:500] + "...",  # Truncate for display
                'metadata': result.payload.get('metadata')
            })
        
        return formatted_results
    
    def test_search(self):
        """Test the search functionality with sample queries"""
        print(f"\n{'='*60}")
        print("Testing Search Functionality")
        print(f"{'='*60}\n")
        
        test_queries = [
            "What cacti can survive in Phoenix summer heat?",
            "How to care for saguaro cactus?",
            "Desert plants that need minimal water",
            "Native plants for Arizona landscaping"
        ]
        
        for query in test_queries:
            print(f"\nQuery: '{query}'")
            print("-" * 60)
            results = self.search(query, limit=3)
            
            for i, result in enumerate(results, 1):
                print(f"\n{i}. {result['title']} (Score: {result['score']:.3f})")
                print(f"   Type: {result['type']} | Source: {result['source']}")
                print(f"   Preview: {result['content'][:200]}...")

if __name__ == "__main__":
    # Configuration
    DATASET_PATH = "data-preparation/arizona_plants_unified_20251018.jsonl"
    EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # Fast and efficient
    QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")

    # Alternative models (uncomment to use):
    # EMBEDDING_MODEL = "all-mpnet-base-v2"  # Better quality, slower
    # EMBEDDING_MODEL = "multi-qa-MiniLM-L6-cos-v1"  # Optimized for Q&A

    try:
        # Initialize vector store
        vector_store = ArizonaPlantVectorStore(
            embedding_model_name=EMBEDDING_MODEL,
            collection_name='arizona_plants',
            qdrant_url=QDRANT_URL
        )
        
        # Build the index
        vector_store.build_index(DATASET_PATH)
        
        # Test search
        vector_store.test_search()
        
        print("\n" + "="*60)
        print("Setup complete! Your vector store is ready.")
        print("="*60)
        print("\nYou can now use vector_store.search(query) to search your documents.")
        print("\nExample:")
        print("  results = vector_store.search('how to water desert plants', limit=5)")
        
    except FileNotFoundError as e:
        print(f"\n✗ Error: {e}")
        print("\nMake sure you have run the data integration script first!")
        print("Expected file: arizona_plants_unified_YYYYMMDD.jsonl")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()