"""
Translation Memory 관리 시스템
- SQLite 기반 TM 저장
- 유사 문장 검색
- 품질 점수 관리
"""

import sqlite3
import hashlib
from typing import List, Dict, Tuple
from pathlib import Path
from difflib import SequenceMatcher


class TranslationMemory:
    """Translation Memory 관리자"""

    def __init__(self, db_path: str = "data/translation_memory.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = None
        self._init_database()

    def _init_database(self):
        """데이터베이스 초기화"""
        self.conn = sqlite3.connect(str(self.db_path))
        cursor = self.conn.cursor()

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS translation_memory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_text TEXT NOT NULL,
            target_text TEXT NOT NULL,
            source_hash TEXT UNIQUE,
            domain TEXT,
            document_type TEXT,
            quality_score INTEGER DEFAULT 5,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_source_hash ON translation_memory(source_hash)
        ''')

        cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_domain ON translation_memory(domain)
        ''')

        self.conn.commit()

    def _calculate_hash(self, text: str) -> str:
        """텍스트 해시 계산"""
        return hashlib.md5(text.encode('utf-8')).hexdigest()

    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """텍스트 유사도 계산 (0.0 ~ 1.0)"""
        return SequenceMatcher(None, text1, text2).ratio()

    def add(self, source: str, target: str, domain: str = "general",
            document_type: str = "claim", quality_score: int = 5) -> bool:
        """TM 추가"""
        try:
            source_hash = self._calculate_hash(source)

            cursor = self.conn.cursor()
            cursor.execute('''
            INSERT OR REPLACE INTO translation_memory
            (source_text, target_text, source_hash, domain, document_type, quality_score)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (source, target, source_hash, domain, document_type, quality_score))

            self.conn.commit()
            return True

        except Exception as e:
            print(f"TM 추가 오류: {e}")
            return False

    def search(self, source: str, domain: str = None,
               similarity_threshold: float = 0.85,
               max_results: int = 5) -> List[Dict]:
        """유사 문장 검색"""
        cursor = self.conn.cursor()

        # 정확히 일치하는 항목 먼저 검색
        source_hash = self._calculate_hash(source)
        cursor.execute('''
        SELECT source_text, target_text, domain, quality_score, 1.0 as similarity
        FROM translation_memory
        WHERE source_hash = ?
        ''', (source_hash,))

        exact_match = cursor.fetchone()
        if exact_match:
            return [{
                "source": exact_match[0],
                "target": exact_match[1],
                "domain": exact_match[2],
                "quality_score": exact_match[3],
                "similarity": 1.0,
                "match_type": "exact"
            }]

        # 도메인 필터
        if domain:
            query = '''
            SELECT source_text, target_text, domain, quality_score
            FROM translation_memory
            WHERE domain = ?
            ORDER BY quality_score DESC
            LIMIT 100
            '''
            cursor.execute(query, (domain,))
        else:
            query = '''
            SELECT source_text, target_text, domain, quality_score
            FROM translation_memory
            ORDER BY quality_score DESC
            LIMIT 100
            '''
            cursor.execute(query)

        candidates = cursor.fetchall()

        # 유사도 계산
        results = []
        for candidate in candidates:
            similarity = self._calculate_similarity(source, candidate[0])
            if similarity >= similarity_threshold:
                results.append({
                    "source": candidate[0],
                    "target": candidate[1],
                    "domain": candidate[2],
                    "quality_score": candidate[3],
                    "similarity": similarity,
                    "match_type": "fuzzy"
                })

        # 유사도 순 정렬
        results.sort(key=lambda x: x["similarity"], reverse=True)

        return results[:max_results]

    def get_stats(self) -> Dict:
        """TM 통계"""
        cursor = self.conn.cursor()

        # 전체 개수
        cursor.execute('SELECT COUNT(*) FROM translation_memory')
        total = cursor.fetchone()[0]

        # 도메인별 개수
        cursor.execute('''
        SELECT domain, COUNT(*) as count
        FROM translation_memory
        GROUP BY domain
        ''')
        domain_counts = dict(cursor.fetchall())

        # 문서 유형별 개수
        cursor.execute('''
        SELECT document_type, COUNT(*) as count
        FROM translation_memory
        GROUP BY document_type
        ''')
        type_counts = dict(cursor.fetchall())

        return {
            "total": total,
            "by_domain": domain_counts,
            "by_type": type_counts
        }

    def close(self):
        """연결 종료"""
        if self.conn:
            self.conn.close()


if __name__ == "__main__":
    # 테스트
    tm = TranslationMemory()

    # TM 추가
    tm.add(
        source="A method comprising a compound",
        target="화합물을 포함하는 방법",
        domain="chemistry_pharma",
        document_type="claim",
        quality_score=10
    )

    # 검색
    results = tm.search("A method comprising a compound", domain="chemistry_pharma")
    print(f"검색 결과: {len(results)}개")
    for r in results:
        print(f"  유사도: {r['similarity']:.2f}, 타입: {r['match_type']}")
        print(f"  원문: {r['source']}")
        print(f"  번역: {r['target']}\n")

    # 통계
    stats = tm.get_stats()
    print(f"TM 통계: {stats}")

    tm.close()
