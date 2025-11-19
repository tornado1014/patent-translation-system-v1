"""
RAG 기반 스타일 가이드 검색 시스템
- 스타일 가이드를 벡터 DB에 저장
- 번역 시 관련 규칙 검색
"""

import os
from pathlib import Path
from typing import List, Dict
try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    print("⚠️ ChromaDB not available. RAG features will be limited.")


class StyleGuideRAG:
    """스타일 가이드 RAG 시스템"""

    def __init__(self, collection_name: str = "patent_style_guide"):
        self.collection_name = collection_name
        self.client = None
        self.collection = None

        if CHROMADB_AVAILABLE:
            self._init_chromadb()

    def _init_chromadb(self):
        """ChromaDB 초기화"""
        try:
            data_dir = Path("data/style_guide_vectors")
            data_dir.mkdir(parents=True, exist_ok=True)

            self.client = chromadb.PersistentClient(path=str(data_dir))
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name
            )
        except Exception as e:
            print(f"ChromaDB 초기화 오류: {e}")
            CHROMADB_AVAILABLE = False

    def index_style_guide(self, guide_path: str):
        """스타일 가이드 인덱싱"""
        if not CHROMADB_AVAILABLE or not self.collection:
            print("RAG 기능 사용 불가")
            return False

        try:
            with open(guide_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 섹션별로 분할 (간단한 예시)
            sections = content.split('\n## ')

            documents = []
            metadatas = []
            ids = []

            for i, section in enumerate(sections):
                if len(section.strip()) > 50:  # 너무 짧은 섹션 제외
                    documents.append(section[:1000])  # 처음 1000자
                    metadatas.append({"section_id": i})
                    ids.append(f"section_{i}")

            if documents:
                self.collection.add(
                    documents=documents,
                    metadatas=metadatas,
                    ids=ids
                )

                print(f"✅ 스타일 가이드 인덱싱 완료: {len(documents)}개 섹션")
                return True

        except Exception as e:
            print(f"인덱싱 오류: {e}")
            return False

    def search_relevant_rules(self, query: str, top_k: int = 3) -> List[Dict]:
        """관련 규칙 검색"""
        if not CHROMADB_AVAILABLE or not self.collection:
            return []

        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=top_k
            )

            if results and results['documents']:
                return [
                    {"rule": doc, "metadata": meta}
                    for doc, meta in zip(results['documents'][0], results['metadatas'][0])
                ]

            return []

        except Exception as e:
            print(f"검색 오류: {e}")
            return []


if __name__ == "__main__":
    # 테스트 (ChromaDB 설치된 경우만 작동)
    rag = StyleGuideRAG()

    if CHROMADB_AVAILABLE:
        # 스타일 가이드 인덱싱 (경로 수정 필요)
        # rag.index_style_guide("../Style_Guide_for_En-Ko_Patent_Localization_v1.0.md")

        # 검색 테스트
        results = rag.search_relevant_rules("How to translate 'detach'?")
        for r in results:
            print(f"규칙: {r['rule'][:200]}...")
