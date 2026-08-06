from __future__ import annotations

from functools import lru_cache

from langchain_core.embeddings import Embeddings
from sentence_transformers import SentenceTransformer


@lru_cache(maxsize=4)
def _load_model(model_name: str) -> SentenceTransformer:
    return SentenceTransformer(model_name)


class MiniLMEmbeddings(Embeddings):
    def __init__(self, model_name: str):
        # 1. Đổi tên biến chứa object thực sự thành _model
        self._model = _load_model(model_name)
        
        # 2. Tạo một biến model chứa chuỗi string để qua mặt bài test của Ragas
        self.model = model_name

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        # 3. Trỏ lại vào self._model
        embeddings = self._model.encode(texts, normalize_embeddings=True)
        return embeddings.tolist()

    def embed_query(self, text: str) -> list[float]:
        # 4. Trỏ lại vào self._model
        embedding = self._model.encode([text], normalize_embeddings=True)
        return embedding[0].tolist()