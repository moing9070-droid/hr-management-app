import streamlit as st

# 1. 페이지 설정 (최상단 1회 지정)
st.set_page_config(
    page_title="BNK시스템 경영지원부 전용 포털",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. 페이지 정의
# (1) 메인 대시보드 (기본 홈)
dashboard_page = st.Page(
    "pages/dashboard.py", 
    title="메인 대시보드", 
    icon="📊",
    default=True
)

# (2) 근태 대조 분석
attendance_page = st.Page(
    "pages/attendance_analysis.py", 
    title="연도별 근태 대조 분석", 
    icon="📅"
)

#  직무 역량/경력 매칭
career_page = st.Page(
    "pages/career_matching.py", 
    title="직무 역량/경력 매칭", 
    icon="🎯"
)

# (3) 동호회 운영 검증
club_page = st.Page(
    "pages/club_verification.py", 
    title="동호회 운영 검증", 
    icon="👥"
)

# 3. 외부 네비게이션 구조 선언 (메뉴 그룹화)
pg = st.navigation(
    {
        "Overview": [dashboard_page],
        "근태 및 조직 분석": [attendance_page],
        "조직 및 인재 관리": [career_page],
        "복리후생 및 운영": [club_page]
    }
)

# 4. 공통 사이드바 (고정)
with st.sidebar:
    st.title("🏢 HR Portal")
    st.caption("BNK시스템 경영지원부 전용 포털")
    st.markdown("---")

# 5. 선택된 페이지 실행
pg.run()