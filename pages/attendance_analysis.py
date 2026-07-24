import streamlit as st
import pandas as pd
from hr_layout import render_page_header

# 1. 페이지 헤더
render_page_header(
    title="📅 연도별 근태 현황 전년 대비 비교 대조 (직원별)", 
    desc="과거와 최근 연도의 개인별 근태 데이터를 직접 대조하여 직원별 주요 변동 사항 및 특이사항을 도출합니다."
)

# 2. 샘플 데이터 생성 함수 (과거 / 최근 연도)
def get_sample_attendance_data():
    data_past = [
        {"사번": "E1001", "성명": "김철수", "부서명": "IT개발팀", "직위": "책임", "지각": 2, "연장근무_인정H": 120.5},
        {"사번": "E1002", "성명": "이영희", "부서명": "데이터운영팀", "직위": "선임", "지각": 0, "연장근무_인정H": 45.0},
        {"사번": "E1003", "성명": "박민수", "부서명": "IT개발팀", "직위": "선임", "지각": 6, "연장근무_인정H": 88.0},
        {"사번": "E1004", "성명": "정수진", "부서명": "경영지원팀", "직위": "수석", "지각": 1, "연장근무_인정H": 15.0},
        {"사번": "E1005", "성명": "최동현", "부서명": "영업기획팀", "직위": "책임", "지각": 3, "연장근무_인정H": 62.0},
        {"사번": "E1006", "성명": "강지은", "부서명": "HRD팀", "직위": "선임", "지각": 0, "연장근무_인정H": 30.0},
        {"사번": "E1007", "성명": "윤서준", "부서명": "IT개발팀", "직위": "사원", "지각": 4, "연장근무_인정H": 110.0},
        {"사번": "E1008", "성명": "임현우", "부서명": "데이터운영팀", "직위": "책임", "지각": 1, "연장근무_인정H": 75.5},
    ]
    
    data_recent = [
        {"사번": "E1001", "성명": "김철수", "부서명": "IT개발팀", "직위": "책임", "지각": 5, "연장근무_인정H": 145.0},  # 지각 +3, 연장 +24.5
        {"사번": "E1002", "성명": "이영희", "부서명": "데이터운영팀", "직위": "선임", "지각": 1, "연장근무_인정H": 40.0},   # 지각 +1, 연장 -5
        {"사번": "E1003", "성명": "박민수", "부서명": "IT개발팀", "직위": "선임", "지각": 8, "연장근무_인정H": 105.0},  # 지각 +2, 연장 +17 (집중케어 대상)
        {"사번": "E1004", "성명": "정수진", "부서명": "경영지원팀", "직위": "수석", "지각": 0, "연장근무_인정H": 12.0},   # 지각 -1, 연장 -3
        {"사번": "E1005", "성명": "최동현", "부서명": "영업기획팀", "직위": "책임", "지각": 7, "연장근무_인정H": 95.0},   # 지각 +4, 연장 +33 (집중케어 대상)
        {"사번": "E1006", "성명": "강지은", "부서명": "HRD팀", "직위": "선임", "지각": 0, "연장근무_인정H": 32.0},   # 변동 거의 없음
        {"사번": "E1007", "성명": "윤서준", "부서명": "IT개발팀", "직위": "사원", "지각": 6, "연장근무_인정H": 150.0},  # 지각 +2, 연장 +40 (집중케어 대상)
        {"사번": "E1008", "성명": "임현우", "부서명": "데이터운영팀", "직위": "책임", "지각": 2, "연장근무_인정H": 80.0},   # 지각 +1, 연장 +4.5
    ]
    
    df_past = pd.DataFrame(data_past)
    df_recent = pd.DataFrame(data_recent)
    
    for df in [df_past, df_recent]:
        df["사번"] = df["사번"].astype(str).str.strip()
        df["부서명_clean"] = df["부서명"].astype(str).str.strip()
        
    return df_past, df_recent

# 3. 엑셀 파싱 함수
def parse_attendance_data(file):
    df_raw = pd.read_excel(file, header=None)
    
    # '사번' 키워드가 들어간 행 자동 탐색
    header_idx = None
    for idx, row in df_raw.iterrows():
        if row.astype(str).str.contains("사번").any():
            header_idx = idx
            break
            
    if header_idx is None:
        raise ValueError("'사번' 컬럼을 찾을 수 없습니다. 엑셀 서식을 확인해 주세요.")
        
    headers = [str(c).strip() for c in df_raw.iloc[header_idx].values]
    df = df_raw.iloc[header_idx + 1:].copy()
    df.columns = headers
    
    # 14번 컬럼(연장근무 인정H) 구체화
    cols = list(df.columns)
    if len(cols) > 14 and cols[14] in ["인정H", "nan"]:
        cols[14] = "연장근무_인정H"
    df.columns = cols
    
    # 기본 데이터 전처리
    df["사번"] = df["사번"].astype(str).str.strip()
    df["부서명_clean"] = df["부서명"].astype(str).str.strip()
    
    # 수치형 변환
    df["지각"] = pd.to_numeric(df["지각"], errors='coerce').fillna(0)
    overtime_col = "연장근무_인정H" if "연장근무_인정H" in df.columns else "지각"
    df["연장근무_인정H"] = pd.to_numeric(df[overtime_col], errors='coerce').fillna(0)
    
    return df

# 4. 업로드 영역
col_f1, col_f2 = st.columns(2)
with col_f1:
    past_file = st.file_uploader("1️⃣ 과거 연도 근태 데이터 (.xlsx)", type=["xlsx"])
with col_f2:
    recent_file = st.file_uploader("2️⃣ 최근 연도 근태 데이터 (.xlsx)", type=["xlsx"])

# 데이터 로드 처리
is_sample = False
df_past, df_recent = None, None

if past_file and recent_file:
    try:
        df_past = parse_attendance_data(past_file)
        df_recent = parse_attendance_data(recent_file)
    except Exception as e:
        st.error(f"파일을 처리하는 과정에서 에러가 발생했습니다: {e}")
else:
    df_past, df_recent = get_sample_attendance_data()
    is_sample = True

# 5. 데이터 처리 및 직원별 비교 분석
if df_past is not None and df_recent is not None:
    if is_sample:
        st.info("💡 **샘플 체험 모드:** 과거(2023년) vs 최근(2024년) 샘플 데이터로 미리 동작하는 화면입니다. 상단에 2개의 엑셀 파일을 업로드하면 실제 데이터로 전환됩니다.")

    # ----------------------------------------------------
    # 📌 1. 전사 핵심 지표 요약 (Metric)
    # ----------------------------------------------------
    st.markdown("### 📌 전사 근태 핵심 지표 변동 요약")
    
    tot_lateness_past = df_past["지각"].sum()
    tot_lateness_recent = df_recent["지각"].sum()
    diff_lateness = tot_lateness_recent - tot_lateness_past
    
    avg_ot_past = df_past["연장근무_인정H"].mean()
    avg_ot_recent = df_recent["연장근무_인정H"].mean()
    diff_ot = avg_ot_recent - avg_ot_past
    
    m1, m2, m3 = st.columns(3)
    m1.metric("총 지각 발생 건수", f"{int(tot_lateness_recent)}건", f"{diff_lateness:+d}건 (전년 대비)")
    m2.metric("인당 평균 연장근무", f"{avg_ot_recent:.1f} 시간", f"{diff_ot:+.1f} 시간 (전년 대비)")
    m3.metric("총 대상 인원", f"{len(df_recent)}명", f"전년 {len(df_past)}명")

    st.markdown("---")

    # ----------------------------------------------------
    # 👤 2. 직원별 전년 대비 근태 지표 대조표
    # ----------------------------------------------------
    st.markdown("### 📋 직원별 전년 대비 근태 지표 대조표")
    
    # 사번 기준 과거/최근 데이터 병합
    df_user_comp = pd.merge(
        df_recent[["사번", "성명", "부서명_clean", "직위", "지각", "연장근무_인정H"]],
        df_past[["사번", "지각", "연장근무_인정H"]],
        on="사번",
        how="inner",
        suffixes=("_최근", "_과거")
    )
    
    # 변동폭 계산
    df_user_comp["지각 변동(건)"] = df_user_comp["지각_최근"] - df_user_comp["지각_과거"]
    df_user_comp["연장근무 변동(h)"] = df_user_comp["연장근무_인정H_최근"] - df_user_comp["연장근무_인정H_과거"]
    
    # 검색 및 필터 옵션
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        search_name = st.text_input("🔍 이름/사번 검색", "")
    with col_s2:
        filter_option = st.selectbox("📌 조회 조건", ["전체 보기", "지각 증가자만 보기", "연장근무 증가자만 보기"])
        
    # 필터링 적용
    df_filtered_display = df_user_comp.copy()
    if search_name:
        df_filtered_display = df_filtered_display[
            df_filtered_display["성명"].str.contains(search_name, na=False) |
            df_filtered_display["사번"].str.contains(search_name, na=False)
        ]
        
    if filter_option == "지각 증가자만 보기":
        df_filtered_display = df_filtered_display[df_filtered_display["지각 변동(건)"] > 0]
    elif filter_option == "연장근무 증가자만 보기":
        df_filtered_display = df_filtered_display[df_filtered_display["연장근무 변동(h)"] > 0]
        
    # 출력 표 컬럼 및 명칭 정리
    df_display = df_filtered_display[[
        "사번", "성명", "부서명_clean", "직위", 
        "지각_과거", "지각_최근", "지각 변동(건)",
        "연장근무_인정H_과거", "연장근무_인정H_최근", "연장근무 변동(h)"
    ]].copy()
    
    df_display.columns = [
        "사번", "성명", "부서", "직위", 
        "과거 지각(건)", "최근 지각(건)", "지각 증감(건)",
        "과거 연장(h)", "최근 연장(h)", "연장 증감(h)"
    ]
    
    # 정수/소수점 포맷 정리
    df_display["과거 지각(건)"] = df_display["과거 지각(건)"].astype(int)
    df_display["최근 지각(건)"] = df_display["최근 지각(건)"].astype(int)
    df_display["지각 증감(건)"] = df_display["지각 증감(건)"].astype(int)
    df_display["과거 연장(h)"] = df_display["과거 연장(h)"].round(1)
    df_display["최근 연장(h)"] = df_display["최근 연장(h)"].round(1)
    df_display["연장 증감(h)"] = df_display["연장 증감(h)"].round(1)

    st.dataframe(df_display, use_container_width=True, hide_index=True)

    st.markdown("---")

    # ----------------------------------------------------
    # 🚨 3. 주요 특이사항 도출 (개인 기준 Top 5)
    # ----------------------------------------------------
    st.markdown("### 🔍 주요 개인별 특이사항")
    
    col_t1, col_t2 = st.columns(2)
    
    # 지각 최다 증가자 Top 5
    with col_t1:
        st.markdown("#### 🚩 전년 대비 지각 최다 증가자 Top 5")
        top_lateness = df_user_comp.sort_values(by="지각 변동(건)", ascending=False).head(5)
        top_lateness = top_lateness[top_lateness["지각 변동(건)"] > 0]
        
        if not top_lateness.empty:
            for _, row in top_lateness.iterrows():
                st.error(f"**{row['성명']}** ({row['부서명_clean']} / {row['직위']}): 지각 **+{int(row['지각 변동(건)'])}건** (최근 {int(row['지각_최근'])}건)")
        else:
            st.success("✅ 전년 대비 지각이 증가한 직원이 없습니다.")

    # 연장근무 최다 증가자 Top 5
    with col_t2:
        st.markdown("#### ⏱️ 전년 대비 연장근무 최다 증가자 Top 5")
        top_ot = df_user_comp.sort_values(by="연장근무 변동(h)", ascending=False).head(5)
        top_ot = top_ot[top_ot["연장근무 변동(h)"] > 0]
        
        if not top_ot.empty:
            for _, row in top_ot.iterrows():
                st.warning(f"**{row['성명']}** ({row['부서명_clean']} / {row['직위']}): 연장근무 **+{row['연장근무 변동(h)']:.1f}시간** (최근 {row['연장근무_인정H_최근']:.1f}h)")
        else:
            st.info("✅ 전년 대비 연장근무가 증가한 직원이 없습니다.")

    st.markdown("<br>", unsafe_allow_html=True)

    # ----------------------------------------------------
    # 👤 4. 최근 연도 지각 5회 이상 집중케어 대상자 명단
    # ----------------------------------------------------
    st.markdown("### ⚠️ 연간 집중케어 대상자 명단 (최근 연도 지각 5회 이상)")
    
    df_care = df_user_comp[df_user_comp["지각_최근"] >= 5].copy()
    
    if not df_care.empty:
        df_care_display = df_care[[
            "사번", "성명", "부서명_clean", "직위", "지각_과거", "지각_최근", "지각 변동(건)"
        ]].rename(columns={
            "부서명_clean": "부서",
            "지각_과거": "과거 지각(건)",
            "지각_최근": "최근 지각(건)",
            "지각 변동(건)": "지각 증감(건)"
        })
        df_care_display["과거 지각(건)"] = df_care_display["과거 지각(건)"].astype(int)
        df_care_display["최근 지각(건)"] = df_care_display["최근 지각(건)"].astype(int)
        df_care_display["지각 증감(건)"] = df_care_display["지각 증감(건)"].astype(int)
        
        st.dataframe(df_care_display, use_container_width=True, hide_index=True)
    else:
        st.success("✅ 최근 연도 기준 지각 5회 이상인 집중케어 대상자가 없습니다.")