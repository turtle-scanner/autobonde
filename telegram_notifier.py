import requests
import logging
import os

# 로깅 설정
logger = logging.getLogger(__name__)

def send_telegram_message(message: str):
    """
    텔레그램으로 메시지를 전송합니다.
    .streamlit/secrets.toml 또는 환경 변수에서 설정을 읽어옵니다.
    """
    token = os.environ.get("TELEGRAM_TOKEN", "")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "")
    
    if not token or not chat_id:
        logger.error("TELEGRAM_TOKEN 또는 TELEGRAM_CHAT_ID가 설정되지 않았습니다.")
        return False
    
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown"
    }
    
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            logger.info("텔레그램 메시지 전송 성공")
            return True
        else:
            logger.error(f"텔레그램 메시지 전송 실패: {response.text}")
            return False
    except Exception as e:
        logger.error(f"텔레그램 전송 중 오류 발생: {e}")
        return False

if __name__ == "__main__":
    # 테스트 메시지
    send_telegram_message("🚀 본데(Bonde) 자동매매 시스템이 시작되었습니다.")
