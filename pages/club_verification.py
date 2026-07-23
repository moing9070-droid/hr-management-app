# pages/club_verification.py
import streamlit as st
import pdfplumber
from pdf2image import convert_from_path
import os
import re
import tempfile
import pandas as pd
from hr_layout import apply_common_layout, render_page_header

st.set_page_config(page_title="동호회 유효회원 검증", layout="wide")

render_page_header(
    title="🔍 동호회 유효회원 검증기", 
    desc="제출된 은행 거래내역서 원본(.pdf)을 분석하여 회원의 회비 납부 연속성 요건을 원클릭으로 정밀 진단합니다."
)

uploaded_file = st.file_uploader("검증할 은행 원본 PDF 파일을 업로드해 주세요.", type=["pdf"])
st.markdown("<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True)

if uploaded_file is not None:
    if "current_file" not in st.session_state or st.session_state["current_file"] != uploaded_file.name:
        st.session_state["current_file"] = uploaded_file.name
        st.session_state["data_loaded"] = False

    if not st.session_state.get("data_loaded", False):
        with st.spinner("📄 PDF 파일 파싱 및 연속성 검증을 진행하고 있습니다..."):
            # 안전한 임시 파일 생성
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                tmp_file.write(uploaded_file.getbuffer())
                tmp_pdf_path = tmp_file.name

            try:
                # ⭕ 핵심 수정: poppler_path 제거 (Streamlit Cloud 및 로컬 OS 자동 인식)
                pdf_images = convert_from_path(tmp_pdf_path, dpi=150)
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
                # 파일 읽기 종료 후 안전하게 임시 파일 삭제
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

    df_display = st.session_state.get("df_final", pd.DataFrame())
    pdf_images = st.session_state.get("pdf_images", [])
    total_pages = len(pdf_images)

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
else:
    st.markdown("""
        <div style="text-align: center; padding: 60px; border: 2px dashed #CBD5E1; border-radius: 12px; background-color: #FFFFFF;">
            <p style="color: #64748B; font-size: 15px; margin: 0;">상단 업로드 바에 파일(.pdf)을 등록하면 자동 검증 시스템이 가동됩니다.</p>
        </div>
    """, unsafe_allow_html=True)