from sentence_transformers import CrossEncoder


class Reranker:
    """
    Cross-encoder reranker.
    Much more accurate than pure vector similarity.
    """

    def __init__(self):
        print("[Reranker] Loading cross-encoder model...")

        # small + fast + strong ranking model
        self.model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

    def rerank(self, question: str, docs: list[str], top_k: int = 3):
        """
        Rerank FAISS candidates by relevance to the question.
        Returns best top_k docs.
        """

        pairs = [(question, d) for d in docs]

        scores = self.model.predict(pairs)

        ranked = sorted(zip(docs, scores),
                        key=lambda x: x[1],
                        reverse=True)
        
        return ranked[:top_k]