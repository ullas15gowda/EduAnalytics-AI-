import os
import glob
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from backend.data_generator import RAG_DIR

class RAGRetriever:
    def __init__(self):
        self.documents = []
        self.chunks = []
        self.vectorizer = None
        self.tfidf_matrix = None
        self.load_and_chunk_documents()
        
    def load_and_chunk_documents(self):
        txt_files = glob.glob(os.path.join(RAG_DIR, "*.txt"))
        self.chunks = []
        
        for filepath in txt_files:
            filename = os.path.basename(filepath)
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
                
            # Chunking document into sections by double newline
            sections = [s.strip() for s in content.split("\n\n") if s.strip()]
            for idx, sec in enumerate(sections):
                self.chunks.append({
                    "chunk_id": f"{filename}_chunk_{idx}",
                    "document_name": filename.replace(".txt", "").replace("_", " "),
                    "filename": filename,
                    "section_num": idx + 1,
                    "text": sec,
                    "verification_date": "2025-01-15"
                })
                
        if self.chunks:
            texts = [c["text"] for c in self.chunks]
            self.vectorizer = TfidfVectorizer(stop_words="english")
            self.tfidf_matrix = self.vectorizer.fit_transform(texts)
            print(f"RAG Engine initialized with {len(self.chunks)} knowledge chunks.")

    def search(self, query: str, top_k: int = 3):
        if not self.chunks or not self.vectorizer:
            return []
            
        query_vec = self.vectorizer.transform([query])
        similarities = cosine_similarity(query_vec, self.tfidf_matrix)[0]
        
        top_indices = similarities.argsort()[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            score = float(similarities[idx])
            if score > 0.05:  # Relevance threshold
                chunk = self.chunks[idx].copy()
                chunk["relevance_score"] = round(score, 4)
                results.append(chunk)
                
        return results

rag_instance = RAGRetriever()

def query_rag_system(user_query: str):
    retrieved_chunks = rag_instance.search(user_query, top_k=2)
    
    if not retrieved_chunks:
        return {
            "answer": "No verified admission documents matched your query directly. Please check JoSAA or state counseling portals for specific details.",
            "sources": [],
            "grounded": False
        }
        
    context_str = "\n\n".join([c["text"] for c in retrieved_chunks])
    
    # Grounded Answer generation
    answer = f"Based on official admission documentation:\n\n"
    for c in retrieved_chunks:
        answer += f"• **[{c['document_name']}]**: {c['text'][:250]}...\n\n"
        
    sources = [{
        "document_name": c["document_name"],
        "filename": c["filename"],
        "section": c["section_num"],
        "verification_date": c["verification_date"],
        "relevance_score": c["relevance_score"]
    } for c in retrieved_chunks]
    
    return {
        "answer": answer.strip(),
        "context": context_str,
        "sources": sources,
        "grounded": True
    }

if __name__ == "__main__":
    res = query_rag_system("What is the fee structure for management quota in Karnataka?")
    print("RAG Search Output:", res)
