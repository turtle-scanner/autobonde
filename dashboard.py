import streamlit as st
import pandas as pd
import sys
import os
from datetime import datetime

# 프로젝트 경로 추가
sys.path.append(os.path.join(os.getcwd(), "strategy_builder"))

import kis_auth as ka
from core import data_fetcher
from examples_user.overseas_stock.overseas_stock_functions import foreign_margin

# 페이지 설정
st.set_page_config(
    page_title="사령부 - 본데 자동매매 대시보드",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 커스텀 CSS (Premium Look)
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
    }
    .stMetric {
        background-color: #161b22;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #30363d;
    }
    .stMetric label {
        color: #8b949e !important;
    }
    .stMetric div {
        color: #58a6ff !important;
    }
    .login-container {
        max-width: 400px;
        margin: 100px auto;
        padding: 40px;
        background-color: #161b22;
        border-radius: 15px;
        border: 1px solid #30363d;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }
    h1, h2, h3 {
        color: #c9d1d9;
    }
    </style>
""", unsafe_allow_html=True)

# 로그인 상태 관리
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# 로그인 페이지
def login_page():
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    st.title("🔒 사령부 접속")
    user_id = st.text_input("아이디", key="user_id")
    password = st.text_input("비밀번호", type="password", key="password")
    
    # 보안 설정: secrets.toml 또는 환경 변수에서 관리자 정보 로드
    admin_id = st.secrets.get("ADMIN_ID", os.environ.get("ADMIN_ID", "cntfed"))
    admin_pw = st.secrets.get("ADMIN_PW", os.environ.get("ADMIN_PW", "cntfed"))
    
    if st.button("로그인", use_container_width=True):
        if user_id == admin_id and password == admin_pw:
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("❌ 아이디 또는 비밀번호가 틀렸습니다.")
    st.markdown('</div>', unsafe_allow_html=True)

# 메인 대시보드
def dashboard_page():
    st.sidebar.title("🚀 BONDE COMMAND")
    # 계좌번호 보안 처리
    acct_no = st.secrets.get("KIS_ACCOUNT_NO", os.environ.get("KIS_ACCOUNT_NO", "46546713-01"))
    st.sidebar.info(f"계좌: {acct_no}")
    if st.sidebar.button("로그아웃"):
        st.session_state.logged_in = False
        st.rerun()

    st.title("📊 실시간 자산 모니터링 (통합증거금)")
    
    # KIS 인증
    try:
        # secrets.toml에서 정보를 읽어오거나 kis_auth 기본 설정 사용
        ka.auth(svr="prod", product="01")
        trenv = ka.getTREnv()
    except Exception as e:
        st.error(f"API 인증 실패: {e}")
        return

    # 데이터 로드
    with st.spinner("자산 정보를 불러오는 중..."):
        # 1. 국내 잔고 (원화)
        domestic_deposit = data_fetcher.get_deposit(env_dv="prod")
        
        # 2. 해외 잔고 (달러) - 통합증거금계좌의 통화별 증거금 조회
        try:
            overseas_margin_df = foreign_margin(cano=trenv.my_acct, acnt_prdt_cd=trenv.my_prod)
            usd_margin = 0.0
            if not overseas_margin_df.empty:
                # USD 데이터 필터링
                usd_row = overseas_margin_df[overseas_margin_df['crcy_cd'] == 'USD']
                if not usd_row.empty:
                    usd_margin = float(usd_row.iloc[0]['frcr_dnca_amt_2']) # 외화예수금
            else:
                usd_margin = 0.0
        except:
            usd_margin = 0.0

    # 상단 요약 지표
    col1, col2, col3, col4 = st.columns(4)
    
    total_equity = domestic_deposit.get('total_eval', 0)
    krw_balance = domestic_deposit.get('deposit', 0)
    profit_loss = domestic_deposit.get('profit_loss', 0)
    
    # 수익률 계산
    if total_equity - profit_loss > 0:
        profit_rate = (profit_loss / (total_equity - profit_loss)) * 100
    else:
        profit_rate = 0.0

    with col1:
        st.metric("총합 자산", f"{total_equity:,} 원", f"{profit_rate:+.2f}%")
    
    with col2:
        st.metric("원화 (KRW)", f"{krw_balance:,} 원")
        
    with col3:
        st.metric("달러 (USD)", f"${usd_margin:,.2f}")
        
    with col4:
        st.metric("총 손익", f"{profit_loss:+,} 원")

    st.divider()

    # 상세 보유 종목
    st.subheader("📋 보유 종목 리스트")
    holdings_df = data_fetcher.get_holdings(env_dv="prod")
    
    if not holdings_df.empty:
        # 보기 좋게 포맷팅
        display_df = holdings_df[['stock_name', 'quantity', 'avg_price', 'current_price', 'profit_rate', 'profit_loss']]
        display_df.columns = ['종목명', '수량', '평균단가', '현재가', '수익률(%)', '평가손익']
        st.dataframe(display_df.style.format({
            '평균단가': '{:,}',
            '현재가': '{:,}',
            '수익률(%)': '{:+.2f}',
            '평가손익': '{:+,}'
        }), use_container_width=True)
    else:
        st.info("현재 보유 중인 종목이 없습니다.")

    # 하단 상태 바
    st.markdown("---")
    st.caption(f"마지막 업데이트: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 본데 전략 엔진 가동 중")

# 페이지 라우팅
if not st.session_state.logged_in:
    login_page()
else:
    dashboard_page()
