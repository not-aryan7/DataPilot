import os


class Retriever:
    """
    Schema retriever.

    Cloud mode: passes all schema docs directly (schemas are small,
    the 70B model handles them easily, no vector search needed).

    Local mode: uses FAISS + cross-encoder for semantic retrieval.
    """

    def __init__(self, schema_docs: list[str]):
        self.schema_docs = schema_docs
        self._use_local = os.environ.get("USE_LOCAL_RAG", "").lower() == "true"

        if self._use_local:
            from .embed import Embedder
            from .index import VectorIndex
            from .reranker import Reranker

            print("[Retriever] Initializing local RAG...")
            self.embedder = Embedder()
            embeddings = self.embedder.encode(schema_docs, prefix="passage")
            self.index = VectorIndex(embeddings.shape[1])
            self.index.add(embeddings, schema_docs)
            self.reranker = Reranker()
            print("[Retriever] Ready.")
        else:
            print("[Retriever] Using lightweight mode (all schema docs passed to LLM).")

    def retrieve(self, question: str, k: int = 10, final_k: int = 3):
        if not self._use_local:
            return self.schema_docs

        query_vec = self.embedder.encode(question, prefix="query")
        candidates = self.index.search(query_vec, k)
        ranked = self.reranker.rerank(question, candidates, final_k)

        MIN_SCORE = 0.2
        filtered = [doc for doc, score in ranked if score >= MIN_SCORE]
        return filtered if filtered else [ranked[0][0]]
