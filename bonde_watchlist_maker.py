import sys
import os
import json
import logging
from datetime import datetime

# 프로젝트 경로 추가
sys.path.append(os.path.join(os.getcwd(), "strategy_builder"))

import kis_auth as ka
from core import data_fetcher

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def generate_bonde_watchlist():
    """
    본데(Stockbee) 유니버스 압축:
    1. 시가총액 100억 달러(약 13조 원) 미만
    2. 유동성 (최근 거래량 10만 주 이상)
    3. 일반 보통주 위주
    """
    logger.info("🚀 본데 유니버스(Watchlist) 생성 시작...")
    
    # 1. KIS 인증 (인증이 안 되어 있으면 수행)
    try:
        ka.auth(svr="prod", product="01")
    except Exception as e:
        logger.error(f"인증 실패: {e}")
        return

    # 샘플에서는 시가총액 필터링을 위해 코스피/코스닥 주요 종목 리스트를 먼저 가져옵니다.
    # 실제로는 전체 종목 마스터 파일을 읽어 필터링하는 것이 좋으나, 
    # 여기서는 상위 500개 종목을 대상으로 1차 필터링을 시연합니다.
    
    # 예시 종목 리스트 (실제로는 마스터 파일 등에서 수천 개를 가져와야 함)
    # 여기서는 편의상 시가총액이 적절한 중소형주 위주로 탐색하는 로직의 골격만 제공합니다.
    
    base_tickers = [
        ("005930", "삼성전자"), ("000660", "SK하이닉스"), ("068270", "셀트리온"), 
        ("196170", "알테오젠"), ("005380", "현대차"), ("035420", "NAVER"),
        ("000270", "기아"), ("105560", "KB금융"), ("055550", "신한지주"),
        # ... 수많은 중소형주가 포함되어야 함
    ]
    
    # 실제 환경에서는 strategy_builder의 종목 정보나 API를 통해 전체 종목을 순회합니다.
    # 여기서는 본데의 '압축' 철학을 보여주기 위해 Watchlist 파일 구조를 생성합니다.
    
    watchlist = []
    
    # 시가총액 및 유동성 필터링 (의사코드 형태 - 실제 API 호출 포함)
    for code, name in base_tickers:
        try:
            # 현재가 및 시가총액 정보 조회
            price_info = data_fetcher.get_current_price(code)
            if not price_info: continue
            
            # 본데 조건 1: 유동성 (최근 거래량 10만 주 이상)
            if price_info.get('volume', 0) < 100000:
                continue
                
            # 본데 조건 2: 시가총액 (13조 원 미만 선호)
            # KIS API에서 시가총액(sigatotal)을 가져오려면 별도 TR이 필요할 수 있습니다.
            # 여기서는 예시로 모든 종목을 일단 포함시키되, 필터링 로직이 들어갈 자리임을 명시합니다.
            
            watchlist.append({
                "code": code,
                "name": name,
                "last_update": datetime.now().strftime("%Y-%m-%d")
            })
            
        except Exception as e:
            logger.warning(f"종목 {name}({code}) 필터링 중 오류: {e}")

    # 파일 저장
    with open("bonde_watchlist.json", "w", encoding="utf-8") as f:
        json.dump(watchlist, f, ensure_ascii=False, indent=4)
        
    logger.info(f"✅ 본데 유니버스 압축 완료: {len(watchlist)} 종목 저장됨 (bonde_watchlist.json)")

if __name__ == "__main__":
    generate_bonde_watchlist()
