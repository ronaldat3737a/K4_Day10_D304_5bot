from __future__ import annotations

import logging
import re
from dataclasses import dataclass

# Lưu ý: Đảm bảo đường dẫn import này khớp với cách bạn setup
from core.config import Settings
from core.utils import first_sentence
from retrieval.index import LocalEmbeddingIndex, SearchResult
from retrieval.llm import build_llm

logger = logging.getLogger(__name__)

@dataclass(frozen=True)
class AnswerResult:
    question: str
    answer: str
    retrieved_doc_ids: list[str]
    retrieved_contexts: list[str]
    retrieved_titles: list[str]


def _extract_answer(question: str, top_result: SearchResult) -> str:
    """Phương pháp trích xuất hiện tại (giữ lại làm dự phòng)."""
    lowered = question.lower()
    metadata = top_result.metadata
    
    if "who authored" in lowered or "list the authors" in lowered:
        return metadata.get("authors_joined", "")
    if "when was" in lowered or "publication date" in lowered or "published on" in lowered:
        return metadata.get("published", "")
    if "what categories" in lowered:
        return metadata.get("categories_joined", "")
        
    return first_sentence(metadata.get("summary", ""))


def _generate_answer_with_llm(question: str, context: str, llm) -> str:
    """Sinh câu trả lời bằng LLM dựa trên ngữ cảnh."""
    # CẬP NHẬT: Ép prompt gắt gao hơn để LLM trả lời thật ngắn gọn
    prompt = f"""Based on the following context, answer the question.
CRITICAL INSTRUCTION: Your answer must be extremely concise. Extract ONLY the exact facts requested. Do NOT say 'Based on the context' or write full sentences if a short phrase is enough.

Context:
{context}

Question: {question}

Answer:"""
    try:
        response = llm.invoke(prompt)
        return getattr(response, 'content', str(response)).strip()
    except Exception as e:
        # Ghi log lỗi để dễ debug thay vì nuốt lỗi hoàn toàn
        logger.error(f"LLM generation failed for question '{question}': {e}")
        return ""


def answer_question(
    question: str, 
    settings: Settings, 
    index: LocalEmbeddingIndex, 
    top_k: int | None = None
) -> AnswerResult:
    """Trả lời câu hỏi bằng cách kết hợp truy xuất và sinh câu trả lời bằng LLM."""
    
    # 1. RETRIEVAL (Truy xuất tài liệu)
    title_match = re.search(r"'([^']+)'", question)
    exact = index.lookup(title_match.group(1)) if title_match else None
    retrieved = index.search(question, top_k=top_k)
    
    if exact:
        exact_result = SearchResult(
            paper_id=exact["paper_id"],
            title=exact["title"],
            score=1.0,
            content=exact["content"],
            metadata=exact["metadata"],
        )
        deduped = [exact_result] + [item for item in retrieved if item.paper_id != exact_result.paper_id]
        retrieved = deduped[: (top_k or settings.top_k)]
    
    # 2. GENERATION (Sinh câu trả lời)
    if not retrieved:
        return AnswerResult(
            question=question,
            answer="I don't know from the indexed corpus.",
            retrieved_doc_ids=[],
            retrieved_contexts=[],
            retrieved_titles=[],
        )

    # Khởi tạo LLM 1 lần duy nhất trong luồng chạy này (Tối ưu performance)
    llm = build_llm(settings=settings, temperature=0.0)
    
    # CẬP NHẬT: Đưa thêm metadata (Tác giả, Ngày tháng) vào Context
    context_parts = []
    for item in retrieved:
        authors = item.metadata.get("authors_joined", "Unknown")
        published = item.metadata.get("published", "Unknown")
        
        doc_text = (
            f"Title: {item.title}\n"
            f"Authors: {authors}\n"
            f"Publication Date: {published}\n"
            f"Content: {item.content}"
        )
        context_parts.append(doc_text)
        
    context = "\n\n---\n\n".join(context_parts)
    
    # Thử gọi LLM
    llm_answer = _generate_answer_with_llm(question, context, llm)
    
    # Fallback nếu LLM thất bại
    if not llm_answer:
        llm_answer = _extract_answer(question, retrieved[0])
        
    return AnswerResult(
        question=question,
        answer=llm_answer,
        retrieved_doc_ids=[item.paper_id for item in retrieved],
        retrieved_contexts=[item.content for item in retrieved],
        retrieved_titles=[item.title for item in retrieved],
    )