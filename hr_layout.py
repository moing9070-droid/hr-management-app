# hr_layout.py
import streamlit as st

def apply_common_layout(page_title="경영지원 Portal"):
    """
    모든 페이지에 동일하게 적용될 스타일 시트, 
    사이드바 브랜딩 영역 및 푸터 정보를 일괄 렌더링합니다.
    """
    # 1. 전역 스타일 테마 선언 (LNB 다크 그레이 프리미엄화)
    st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
            html, body, [data-testid="stAppViewContainer"] {
                font-family: 'Inter', 'Noto Sans KR', sans-serif;
                background-color: #F8FAFC;
            }
            
            /* 사이드바 스타일 */
            [data-testid="stSidebar"] {
                background-color: #0F172A !important;
                padding-top: 20px !important;
            }
            [data-testid="stSidebar"] * {
                color: #E2E8F0 !important;
            }
            
            /* 사이드바 내부 네비게이션 가독성 개선 */
            [data-testid="stSidebarNav"] ul {
                padding-top: 10px !important;
                gap: 8px !important;
            }
            [data-testid="stSidebarNav"] li a {
                background-color: #1E293B !important;
                border: 1px solid #334155 !important;
                border-radius: 8px !important;
                padding: 12px 16px !important;
                font-size: 14px !important;
                font-weight: 500 !important;
                margin: 4px 12px !important;
                transition: all 0.2s ease-in-out !important;
                display: flex !important;
                align-items: center !important;
            }
            [data-testid="stSidebarNav"] li a:hover {
                background-color: #334155 !important;
                border-color: #475569 !important;
                text-decoration: none !important;
            }
            [data-testid="stSidebarNav"] li a[aria-current="page"] {
                background-color: #3B82F6 !important;
                border-color: #3B82F6 !important;
                font-weight: 600 !important;
                color: #FFFFFF !important;
            }

            /* 사이드바 브랜딩 로고 영역 */
            .sidebar-logo-area {
                padding: 10px 20px 20px 20px;
                border-bottom: 1px solid #334155;
                margin-bottom: 16px;
            }
            .sidebar-logo-title {
                font-size: 18px !important;
                font-weight: 700 !important;
                color: #3B82F6 !important;
                letter-spacing: -0.5px;
                margin: 0 !important;
            }
            .sidebar-logo-subtitle {
                font-size: 11px !important;
                color: #94A3B8 !important;
                margin-top: 4px !important;
                margin-bottom: 0 !important;
            }

            /* 메인 콘텐츠 타이틀 헤더 */
            .main-header {
                background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
                padding: 24px 32px;
                border-radius: 12px;
                color: #FFFFFF;
                margin-bottom: 28px;
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            }
            .main-header h1 {
                color: #FFFFFF !important;
                font-size: 24px !important;
                font-weight: 700 !important;
                margin-bottom: 6px !important;
                letter-spacing: -0.5px;
            }
            .main-header p {
                color: #94A3B8 !important;
                font-size: 13px !important;
                margin: 0 !important;
            }
            
            /* 섹션 타이틀 공통 가이드 */
            .section-title {
                font-size: 16px !important;
                font-weight: 600 !important;
                color: #1E293B;
                margin-bottom: 16px;
                display: flex;
                align-items: center;
                gap: 8px;
                border-left: 4px solid #3B82F6;
                padding-left: 12px;
            }
        </style>
    """, unsafe_allow_html=True)

    # 2. 사이드바 내 로고 렌더링
    with st.sidebar:
        st.markdown("""
            <div class="sidebar-logo-area">
                <h1 class="sidebar-logo-title">경영지원 Portal</h1>
                <div class="sidebar-logo-subtitle">사내 운영 효율화 플랫폼</div>
            </div>
        """, unsafe_allow_html=True)
        
        # 3. 사이드바 하단 공통 푸터
        st.markdown("<div style='margin-top: 40px; border-top: 1px solid #334155; padding-top: 20px;'></div>", unsafe_allow_html=True)
        st.markdown("<div style='font-size:11px; color:#64748B; padding: 0 8px;'><b>시스템 분류:</b> 지원 부서 공용<br><b>보안레벨:</b> 사내 내부망 전용</div>", unsafe_allow_html=True)

def render_page_header(title, desc):
    """모든 서브페이지 상단에 깔끔하게 배치될 그라데이션 타이틀 배너입니다."""
    st.markdown(f"""
        <div class="main-header">
            <h1>{title}</h1>
            <p>{desc}</p>
        </div>
    """, unsafe_allow_html=True)