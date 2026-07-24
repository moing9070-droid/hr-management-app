# pages/club_verification.py
import streamlit as st
import pdfplumber
from pdf2image import convert_from_path
import os
import re
import tempfile
import pandas as pd
from pathlib import Path
from hr_layout import apply_common_layout, render_page_header

st.set_page_config(page_title="동호회 유효회원 검증", layout="wide")

render_page_header(
    title="🔍 동호회 유효회원 검증기", 
    desc="제출된 은행 거래내역서 원본(.pdf)을 분석하여 회원의 회비 납부 연속성 요건을 원클릭으로 정밀 진단합니다."
)

uploaded_file = st.file_uploader("검증할 은행 원본 PDF 파일을 업로드해 주세요. (미업로드 시 샘플 데이터로 동작합니다)", type=["pdf"])
st.markdown("<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True)

# ----------------------------------------------------
# [샘플 데이터 정의]
# ----------------------------------------------------
def get_sample_data():
    sample_rows = [
        {"검증상태": "✅ 2개월 연속 완료", "내통장표시/입금자": "김철수(HRD)", "거래일시": "2026-02-05 10:15", "거래금액": 30000, "원본페이지": 1, "적요": "1월 회비"},
        {"검증상태": "✅ 2개월 연속 완료", "내통장표시/입금자": "김철수(HRD)", "거래일시": "2026-01-05 09:30", "거래금액": 30000, "원본페이지": 1, "적요": "12월 회비"},
        {"검증상태": "⚠️ 연속성 미충족", "내통장표시/입금자": "이영희(재무)", "거래일시": "2026-02-10 14:20", "거래금액": 30000, "원본페이지": 1, "적요": "2월 회비"},
        {"검증상태": "✅ 2개월 연속 완료", "내통장표시/입금자": "박민수(IT)", "거래일시": "2026-02-04 18:00", "거래금액": 30000, "원본페이지": 1, "적요": "2월 회비"},
        {"검증상태": "✅ 2개월 연속 완료", "내통장표시/입금자": "박민수(IT)", "거래일시": "2026-01-04 17:45", "거래금액": 30000, "원본페이지": 1, "적요": "1월 회비"}
    ]
    return pd.DataFrame(sample_rows)

# 1. 프로젝트 최상위 디렉토리(Root) 경로 자동 산출
# pages/club_verification.py 기준으로 상위 폴더(..)가 최상위 루트가 됩니다.
BASE_DIR = Path(__file__).resolve().parent.parent

# 2. 프로젝트 루트 내 poppler bin 폴더 상대 경로 지정
# 예: 프로젝트루트/poppler/Library/bin 또는 프로젝트루트/poppler/bin
# 실제로 poppler 내부에서 pdfinfo.exe 파일이 들어있는 bin 폴더 경로를 맞춰주세요.
POPPLER_BIN_DIR = BASE_DIR / "poppler" / "bin"

# 3. 로컬 vs 배포 환경 자동 감지 (poppler_path 조건부 설정)
# 윈도우용 poppler 폴더가 실제 존재하는 경우에만 poppler_path로 전달합니다.
poppler_path_arg = str(POPPLER_BIN_DIR) if POPPLER_BIN_DIR.exists() else None

# ----------------------------------------------------
# [데이터 로딩 로직]
# ----------------------------------------------------
if uploaded_file is not None:
    # 1. 사용자가 직접 파일 업로드한 경우
    if "current_file" not in st.session_state or st.session_state["current_file"] != uploaded_file.name:
        st.session_state["current_file"] = uploaded_file.name
        st.session_state["data_loaded"] = False

    if not st.session_state.get("data_loaded", False):
        with st.spinner("📄 PDF 파일 파싱 및 연속성 검증을 진행하고 있습니다..."):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                tmp_file.write(uploaded_file.getbuffer())
                tmp_pdf_path = tmp_file.name

            try:
                pdf_images = convert_from_path(tmp_pdf_path, dpi=150, poppler_path=poppler_path_arg)
                st.session_state["pdf_images"] = pdf_images
                
                all_rows = []
                with pdfplumber.open(tmp_pdf_path) as pdf:
                    for page_idx, page in enumerate(pdf.pages):
                        tables = page.extract_tables()
                        for table in tables:
                            for row in table:
                                if not row or all(cell is None or str(cell).strip() == "" for cell in row):
                                    continue
                                clean_row = [str(cell).replace("\n", " ").strip() if cell else "" for cell in row]
                                if "거래일" in clean_row[0] or "적요" in clean_row[1]:
                                    continue
                                all_rows.append([page_idx + 1] + clean_row)
            finally:
                if os.path.exists(tmp_pdf_path):
                    os.remove(tmp_pdf_path)

            if all_rows:
                max_cols = max(len(r) for r in all_rows)
                df_raw = pd.DataFrame(all_rows)
                
                columns_mapped = ["원본페이지", "거래일시", "적요", "내통장표시/입금자", "구분", "거래금액", "거래후잔액", "취급점"]
                df_raw.columns = columns_mapped[:max_cols] + [f"열_{i}" for i in range(len(columns_mapped), max_cols)]
                
                if "구분" in df_raw.columns:
                    df_raw = df_raw[df_raw["구분"].str.contains("입금|대체", na=True)]
                
                df_raw["정렬용날짜"] = df_raw["거래일시"].str.extract(r'(\d{2,4}[-./]\d{2}[-./]\d{2})').fillna("0000-00-00")
                df_raw = df_raw[df_raw["내통장표시/입금자"].str.strip() != ""]
                
                months = []
                for dt in df_raw["거래일시"]:
                    match = re.search(r'\d{2,4}[-./](\d{2})[-./]', str(dt))
                    months.append(int(match.group(1)) if match else None)
                df_raw["거래월"] = months
                
                user_month_map = df_raw.dropna(subset=["거래월"]).groupby("내통장표시/입금자")["거래월"].unique()
                
                user_status_map = {}
                for user, m_list in user_month_map.items():
                    sorted_months = sorted(list(m_list))
                    is_consecutive = False
                    for i in range(len(sorted_months) - 1):
                        diff = sorted_months[i+1] - sorted_months[i]
                        if diff == 1 or diff == -11:
                            is_consecutive = True
                            break
                    user_status_map[user] = "✅ 2개월 연속 완료" if is_consecutive else "⚠️ 연속성 미충족"
                
                df_raw["검증상태"] = [user_status_map.get(u, "⚠️ 내역 확인 불가") for u in df_raw["내통장표시/입금자"]]
                df_sorted = df_raw.sort_values(by=["내통장표시/입금자", "정렬용날짜"], ascending=[True, False])
                
                display_cols = ["검증상태", "내통장표시/입금자", "거래일시", "거래금액", "원본페이지", "적요"]
                existing_cols = [c for c in display_cols if c in df_sorted.columns]
                st.session_state["df_final"] = df_sorted[existing_cols]
            else:
                st.session_state["df_final"] = pd.DataFrame()
            
            st.session_state["data_loaded"] = True
            st.session_state["is_sample"] = False
else:
    # 2. 업로드 파일이 없을 때 (초기 진입 시 샘플 데이터 세팅)
    st.session_state["df_final"] = get_sample_data()
    st.session_state["pdf_images"] = []
    st.session_state["is_sample"] = True

# ----------------------------------------------------
# [화면 렌더링 로직]
# ----------------------------------------------------
df_display = st.session_state.get("df_final", pd.DataFrame())
pdf_images = st.session_state.get("pdf_images", [])
total_pages = len(pdf_images)

# 샘플 데이터 동작 중 안내 배너 출력
if st.session_state.get("is_sample", False):
    st.info("💡 **샘플 체험 모드:** 파일 업로드 전 시스템 동작 미리보기 화면입니다. 실제 PDF 파일을 업로드하면 등록된 파일 내용으로 자동 전환됩니다.")

col1, col2 = st.columns([1.0, 1.2], gap="large")

with col1:
    st.markdown("<div class='section-title'>🖼️ 원본 거래내역서 대조</div>", unsafe_allow_html=True)
    if total_pages > 1:
        page_num = st.number_input(f"페이지 이동 (총 {total_pages}쪽)", min_value=1, max_value=total_pages, value=1)
    else:
        page_num = 1
    st.markdown("<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True)
    
    if pdf_images:
        st.image(pdf_images[page_num - 1], use_container_width=True)
    else:
        # 샘플 모드 또는 이미지 없을 때 가상 뷰어 영역 표시
        st.markdown("""
            <div style="text-align: center; padding: 120px 20px; border: 2px dashed #CBD5E1; border-radius: 12px; background-color: #F8FAFC;">
                <p style="color: #64748B; font-size: 14px; margin: 0; font-weight: 500;">
                    📄 PDF 파일 업로드 시<br>원본 문서 스캔 이미지가 이 영역에 동시 렌더링됩니다.
                </p>
            </div>
        """, unsafe_allow_html=True)

with col2:
    tab1, tab2 = st.tabs(["📊 데이터 분석 Grid", "🔍 특정 대상자 집중 추적"])
    
    with tab1:
        st.markdown("<div style='margin-bottom: 16px;'></div>", unsafe_allow_html=True)
        st.markdown("<p style='font-size:13px; color:#475569; background-color:#F1F5F9; padding:12px; border-radius:8px; border-left:3px solid #64748B;'>💡 <b>검증 기준:</b> 실제 달이 연속하여 회비를 입금한 명단만 자동으로 유효 판정 처리됩니다.</p>", unsafe_allow_html=True)
        
        if not df_display.empty:
            st.dataframe(
                df_display, 
                use_container_width=True, 
                height=520,
                column_config={
                    "검증상태": st.column_config.TextColumn("검증 상태", width="medium"),
                    "내통장표시/입금자": "입금자명",
                    "거래금액": st.column_config.NumberColumn("거래 금액", format="%d 원")
                }
            )
            
            csv = df_display.to_csv(index=False).encode('utf-8-sig')
            st.download_button("📥 검증 리포트 추출 (CSV)", data=csv, file_name="bank_verification.csv", mime="text/csv", use_container_width=True)
        else:
            st.info("추출된 거래 내역이 존재하지 않습니다.")

    with tab2:
        st.markdown("<div style='margin-bottom: 16px;'></div>", unsafe_allow_html=True)
        if not df_display.empty:
            user_list = sorted(df_display["내통장표시/입금자"].unique())
            selected_user = st.selectbox("🎯 추적 분석할 대상자를 지정하세요.", ["전체 보기"] + user_list)
            st.markdown("---")
            
            if selected_user != "전체 보기":
                user_df = df_display[df_display["내통장표시/입금자"] == selected_user]
                user_status = user_df["검증상태"].iloc[0]
                if "✅" in user_status:
                    st.success(f"**{selected_user}** 님은 자격 요건을 충족합니다. ({user_status})")
                else:
                    st.warning(f"**{selected_user}** 님은 연속성 요건을 충족하지 못했습니다.")
                st.dataframe(user_df[["검증상태", "거래일시", "거래금액", "원본페이지", "적요"]], use_container_width=True)