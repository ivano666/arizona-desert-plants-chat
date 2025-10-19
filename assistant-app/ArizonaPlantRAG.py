from ArizonaPlantVectorStore import ArizonaPlantVectorStore

from openai import OpenAI

class ArizonaPlantRAG:
    def __init__(self, vector_store: ArizonaPlantVectorStore, openai_client = None):
        self.vector_store = vector_store
        if openai_client:
            self.openai_client = openai_client
        else:
            self.openai_client = OpenAI()
    
    def build_prompt(self, query, search_results):
        """
        Build a prompt for the LLM using retrieved documents
        
        Args:
            query: User's question
            search_results: List of relevant documents from vector search
            
        Returns:
            Formatted prompt string
        """
        # Build context from search results
        context_parts = []
        
        for i, result in enumerate(search_results, 1):
            context_parts.append(f"Document {i} (Score: {result['score']:.3f}):")
            context_parts.append(f"Title: {result['title']}")
            context_parts.append(f"Source: {result['source']}")
            context_parts.append(f"Content: {result['content']}")
            context_parts.append("")  # blank line
        
        context = "\n".join(context_parts)
        
        # Build the full prompt
        prompt = f"""You are an expert on Arizona desert plants. Answer the user's question based on the provided context from authoritative sources.

        Context from relevant documents:
        {context}

        User Question: {query}

        Instructions:
        - Provide a clear, detailed answer based on the context above
        - If the context contains scientific names, include them
        - If mentioning care instructions, be specific about Arizona conditions
        - If the context doesn't fully answer the question, say so
        - Cite which document(s) you're drawing from (e.g., "According to Document 1...")

        Answer:""".strip()
        
        return prompt


    def llm(self, prompt):
        """
        Call OpenAI API to generate answer
        
        Args:
            prompt: Full prompt with context and question
            
        Returns:
            Generated answer string
        """
        
        response = self.openai_client.chat.completions.create(
            model='gpt-4o-mini',
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,  # Slightly creative but mostly factual
            max_tokens=500    # Adjust based on your needs
        )
        
        return response.choices[0].message.content


    def rag(self, query):
        """
        Complete RAG pipeline: Retrieve relevant docs and generate answer
        
        Args:
            query: User's question
            vector_store: Initialized ArizonaPlantVectorStore instance
            
        Returns:
            Generated answer string
        """
        # Step 1: Retrieve relevant documents
        print("\n" + "="*60)
        print("RAG Pipeline")
        print("="*60)
        search_results = self.vector_store.search(query, limit=5)
        
        # Step 2: Build prompt with context
        prompt = self.build_prompt(query, search_results)
        
        # Optional: Print prompt for debugging
        # print("\nPrompt being sent to LLM:")
        # print("-"*60)
        # print(prompt)
        # print("-"*60)
        
        # Step 3: Generate answer
        print("Generating answer...")
        answer = self.llm(prompt)
        
        print("✓ Answer generated")
        print("="*60 + "\n")
        
        return answer
