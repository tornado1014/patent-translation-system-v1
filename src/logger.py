"""
특허 번역 시스템 로깅
- 파일 기반 상세 로그
- 콘솔 출력
- 단계별 추적
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional


class TranslationLogger:
    """번역 시스템 전용 로거"""

    def __init__(self, log_dir: str = "logs", console_level: int = logging.INFO):
        """
        Args:
            log_dir: 로그 파일 저장 디렉토리
            console_level: 콘솔 출력 레벨
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)

        # 로거 설정
        self.logger = logging.getLogger("PatentTranslation")
        self.logger.setLevel(logging.DEBUG)
        self.logger.handlers.clear()

        # 파일 핸들러 (상세 로그)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = self.log_dir / f"translation_{timestamp}.log"
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)

        # 콘솔 핸들러 (요약 로그)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(console_level)
        console_formatter = logging.Formatter('%(levelname)s: %(message)s')
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)

        self.current_log_file = log_file
        self.logger.info(f"로거 초기화 완료 - 로그 파일: {log_file}")

    def debug(self, message: str):
        """디버그 레벨 로그"""
        self.logger.debug(message)

    def info(self, message: str):
        """정보 레벨 로그"""
        self.logger.info(message)

    def warning(self, message: str):
        """경고 레벨 로그"""
        self.logger.warning(message)

    def error(self, message: str, exc_info: bool = False):
        """에러 레벨 로그"""
        self.logger.error(message, exc_info=exc_info)

    def critical(self, message: str, exc_info: bool = False):
        """치명적 에러 레벨 로그"""
        self.logger.critical(message, exc_info=exc_info)

    # 번역 단계별 로깅 헬퍼 메서드

    def log_translation_start(self, input_file: str, output_file: str, doc_type: str):
        """번역 시작 로그"""
        self.logger.info("=" * 80)
        self.logger.info("번역 작업 시작")
        self.logger.info(f"  입력 파일: {input_file}")
        self.logger.info(f"  출력 파일: {output_file}")
        self.logger.info(f"  문서 유형: {doc_type}")
        self.logger.info("=" * 80)

    def log_file_read(self, file_path: str, file_type: str, success: bool, error: Optional[str] = None):
        """파일 읽기 로그"""
        if success:
            self.logger.info(f"파일 읽기 성공: {file_path} ({file_type})")
        else:
            self.logger.error(f"파일 읽기 실패: {file_path} ({file_type}) - {error}")

    def log_analysis_start(self):
        """문서 분석 시작"""
        self.logger.info("STEP 1: 문서 분석 시작")

    def log_analysis_result(self, domain: str, term_count: int, patterns: int):
        """문서 분석 결과"""
        self.logger.info(f"  도메인 식별: {domain}")
        self.logger.info(f"  기술 용어 추출: {term_count}개")
        self.logger.info(f"  반복 패턴: {patterns}개")
        self.logger.debug(f"분석 완료 - 도메인: {domain}, 용어: {term_count}, 패턴: {patterns}")

    def log_tm_search(self, query: str, results: int):
        """TM 검색 로그"""
        self.logger.info("STEP 2: Translation Memory 검색")
        self.logger.debug(f"  검색어 길이: {len(query)} 문자")
        if results > 0:
            self.logger.info(f"  TM 매치 발견: {results}개")
        else:
            self.logger.info("  TM 매치 없음")

    def log_translation_phase(self, phase: str, details: str = ""):
        """번역 단계 로그"""
        self.logger.info(f"STEP 3: 번역 수행 - {phase}")
        if details:
            self.logger.debug(f"  {details}")

    def log_api_call(self, model: str, tokens: int, success: bool, error: Optional[str] = None):
        """API 호출 로그"""
        if success:
            self.logger.info(f"  API 호출 성공: {model} (토큰: {tokens})")
            self.logger.debug(f"Claude API 응답 성공 - 모델: {model}, 토큰: {tokens}")
        else:
            self.logger.error(f"  API 호출 실패: {model} - {error}")

    def log_qa_start(self):
        """QA 검증 시작"""
        self.logger.info("STEP 4: 품질 검증 (QA)")

    def log_qa_result(self, violations: int, severity_counts: dict, passed: bool):
        """QA 검증 결과"""
        self.logger.info(f"  총 위반 사항: {violations}개")
        self.logger.info(f"  Critical: {severity_counts.get('critical', 0)}, "
                        f"Major: {severity_counts.get('major', 0)}, "
                        f"Minor: {severity_counts.get('minor', 0)}")
        if passed:
            self.logger.info("  QA 결과: ✅ PASS")
        else:
            self.logger.warning("  QA 결과: ❌ FAIL")

        # 상세 로그
        self.logger.debug(f"QA 검증 완료 - 위반: {violations}, 통과: {passed}")
        for severity, count in severity_counts.items():
            if count > 0:
                self.logger.debug(f"  {severity.upper()}: {count}개")

    def log_tm_save(self, source: str, translation: str, quality: float):
        """TM 저장 로그"""
        self.logger.info("STEP 5: Translation Memory 저장")
        self.logger.debug(f"  원문 길이: {len(source)} 문자")
        self.logger.debug(f"  번역문 길이: {len(translation)} 문자")
        self.logger.debug(f"  품질 점수: {quality}/10")

    def log_file_save(self, file_path: str, file_type: str, success: bool, error: Optional[str] = None):
        """파일 저장 로그"""
        if success:
            self.logger.info(f"파일 저장 성공: {file_path} ({file_type})")
        else:
            self.logger.error(f"파일 저장 실패: {file_path} ({file_type}) - {error}")

    def log_translation_complete(self, success: bool, duration: float = None):
        """번역 완료 로그"""
        self.logger.info("=" * 80)
        if success:
            self.logger.info("번역 작업 완료 ✅")
            if duration:
                self.logger.info(f"  소요 시간: {duration:.2f}초")
        else:
            self.logger.error("번역 작업 실패 ❌")
        self.logger.info("=" * 80)

    def log_section_parsing(self, total_sections: int, section_types: dict):
        """섹션 파싱 로그"""
        self.logger.info("🤖 자동 섹션 분류 모드")
        self.logger.info(f"  총 섹션: {total_sections}개")
        for section_type, count in section_types.items():
            if count > 0:
                self.logger.info(f"  {section_type.upper()}: {count}개")

    def log_section_translation(self, current: int, total: int, section_type: str, doc_type: str):
        """섹션별 번역 로그"""
        self.logger.info(f"번역 중 ({current}/{total}): {section_type.upper()} - {doc_type}")

    def get_log_file_path(self) -> Path:
        """현재 로그 파일 경로 반환"""
        return self.current_log_file

    def close(self):
        """로거 종료"""
        self.logger.info("로거 종료")
        for handler in self.logger.handlers:
            handler.close()
        self.logger.handlers.clear()


# 전역 로거 인스턴스
_global_logger: Optional[TranslationLogger] = None


def get_logger() -> TranslationLogger:
    """전역 로거 인스턴스 반환"""
    global _global_logger
    if _global_logger is None:
        _global_logger = TranslationLogger()
    return _global_logger


def set_logger(logger: TranslationLogger):
    """전역 로거 설정"""
    global _global_logger
    _global_logger = logger


if __name__ == "__main__":
    # 테스트
    logger = TranslationLogger()

    logger.log_translation_start("input.txt", "output.txt", "claim")
    logger.log_file_read("input.txt", "txt", True)
    logger.log_analysis_start()
    logger.log_analysis_result("biotech", 5, 2)
    logger.log_tm_search("sample text", 0)
    logger.log_translation_phase("초벌 번역", "Claude API 호출")
    logger.log_api_call("claude-sonnet-4-5", 1500, True)
    logger.log_qa_start()
    logger.log_qa_result(2, {'critical': 0, 'major': 1, 'minor': 1}, False)
    logger.log_tm_save("source", "translation", 8.5)
    logger.log_file_save("output.txt", "txt", True)
    logger.log_translation_complete(True, 45.3)

    print(f"\n로그 파일: {logger.get_log_file_path()}")
