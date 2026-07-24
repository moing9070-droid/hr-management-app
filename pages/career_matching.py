import streamlit as st
import pandas as pd
from hr_layout import render_page_header

# 1. 페이지 헤더
render_page_header(
    title="🎯 직무 역량/경력 매칭 (Talent Finder)", 
    desc="직원의 기술 스택(OS, DBMS, Language 등) 및 프로젝트 경력을 바탕으로 직무 순환 및 인사 이동 적합자를 검색합니다."
)

# 2. 샘플 데이터 생성 함수
def get_sample_data():
    data = [
        {"사번": "E1001", "성명": "김철수", "부서명": "IT개발팀", "회사명": "A사", "사업/직렬 명": "차세대 시스템 구축", "투입시작일자": "2022-01-01", "투입종료일자": "2023-06-30", "투입개월수": 18, "고객사": "금융 A사", "업무 상세": "카드 승인 백엔드 모듈 개발 및 ERP 연동 API 구축", "IT직무명": "SW개발자", "OS": "Linux", "DBMS": "Oracle", "Tool": "Git", "Language": "Java", "Framework": "Spring Boot", "IT기술 상세": "Java, Spring Boot, Oracle 기반 개발"},
        {"사번": "E1001", "성명": "김철수", "부서명": "IT개발팀", "회사명": "A사", "사업/직렬 명": "회계시스템 고도화", "투입시작일자": "2023-07-01", "투입종료일자": "2024-02-28", "투입개월수": 8, "고객사": "내부", "업무 상세": "회계 전표 처리 모듈 개편 및 DB 최적화", "IT직무명": "SW개발자", "OS": "Linux", "DBMS": "PostgreSQL", "Tool": "Docker", "Language": "Java", "Framework": "Spring", "IT기술 상세": "Java, PostgreSQL"},
        {"사번": "E1002", "성명": "이영희", "부서명": "데이터운영팀", "회사명": "A사", "사업/직렬 명": "데이터 마이그레이션", "투입시작일자": "2022-05-01", "투입종료일자": "2023-12-31", "투입개월수": 20, "고객사": "카드 B사", "업무 상세": "대용량 금융 데이터 이관 및 튜닝, DW 구축", "IT직무명": "DBA", "OS": "Unix", "DBMS": "Oracle", "Tool": "Toad", "Language": "SQL, Python", "Framework": "-", "IT기술 상세": "Oracle, SQL Tuning, Python"},
        {"사번": "E1003", "성명": "박민수", "부서명": "IT개발팀", "회사명": "A사", "사업/직렬 명": "모바일 앱 리뉴얼", "투입시작일자": "2023-01-01", "투입종료일자": "2024-05-31", "투입개월수": 17, "고객사": "유통 C사", "업무 상세": "프론트엔드 UI 개발 및 Node.js 기반 통신 서버 구축", "IT직무명": "Web개발자", "OS": "Windows", "DBMS": "MySQL", "Tool": "VSCode", "Language": "JavaScript, TypeScript", "Framework": "React, Node.js", "IT기술 상세": "React, TypeScript, Node.js"},
        {"사번": "E1004", "성명": "정수진", "부서명": "경영지원팀", "회사명": "A사", "사업/직렬 명": "ERP 기획 및 도입", "투입시작일자": "2021-03-01", "투입종료일자": "2022-12-31", "투입개월수": 22, "고객사": "내부", "업무 상세": "재무회계 및 HR 모듈 요구사항 정의, ERP 프로세스 설계", "IT직무명": "IT기획자", "OS": "-", "DBMS": "-", "Tool": "Jira", "Language": "-", "Framework": "-", "IT기술 상세": "SAP ERP, 인사/회계 프로세스 설계"}
    ]
    df = pd.DataFrame(data)
    df["사번"] = df["사번"].astype(str).str.strip()
    return df

# 3. 업로드 데이터 파싱 함수
def parse_career_file(file):
    df = pd.read_excel(file, skiprows=1)
    if "사번" in df.columns:
        df["사번"] = df["사번"].astype(str).str.strip()
    return df

# 4. 파일 업로드 영역
uploaded_file = st.file_uploader("📂 업무경력 관리 엑셀 파일 업로드 (.xlsx)", type=["xlsx"])

# 💡 [핵심 수정] 파일이 없으면 기본적으로 샘플 데이터가 할당되도록 처리
is_sample = False

if uploaded_file is not None:
    try:
        df_raw = parse_career_file(uploaded_file)
    except Exception as e:
        st.error(f"엑셀 데이터 처리 중 에러가 발생했습니다: {e}")
        df_raw = pd.DataFrame()
else:
    df_raw = get_sample_data()
    is_sample = True

# 5. 메인 화면 출력
if not df_raw.empty:
    if is_sample:
        st.info("💡 **샘플 체험 모드:** 파일 업로드 전 미리보기 화면입니다. 실제 `.xlsx` 파일을 업로드하면 해당 데이터로 자동 전환됩니다.")
    
    # 기본 정보 집계
    total_records = len(df_raw)
    total_employees = df_raw["사번"].nunique() if "사번" in df_raw.columns else 0
    
    st.success(f"✅ 총 **{total_employees}명** (경력 이력 **{total_records}건**)의 데이터가 로드되었습니다.")
    st.markdown("---")
    
    # 6. 검색 필터 설정
    st.markdown("### 🔍 인재 키워드 매칭 검색")
    
    col_s1, col_s2, col_s3 = st.columns([3, 1, 1])
    with col_s1:
        search_input = st.text_input(
            "검색 키워드 입력 (기술, 직무, 업무상세 등)", 
            placeholder="예: Java, Oracle, 회계, 카드, Spring, ERP"
        )
    with col_s2:
        search_mode = st.radio("검색 조건", ["OR (하나라도 포함)", "AND (모두 포함)"])
    with col_s3:
        dept_list = ["전체 부서"] + sorted(list(df_raw["부서명"].dropna().unique())) if "부서명" in df_raw.columns else ["전체"]
        selected_dept = st.selectbox("부서 필터", dept_list)

    # 7. 검색 및 결과 출력
    if search_input:
        keywords = [k.strip() for k in search_input.split(",") if k.strip()]
        
        target_cols = [
            '사업/직렬 명', '고객사', '업무 상세', 'IT직무명', 
            'OS', 'DBMS', 'Tool', 'Language', 'Framework', 'IT기술 상세'
        ]
        search_cols = [c for c in target_cols if c in df_raw.columns]
        
        def check_match(row):
            row_str = " ".join(row[search_cols].fillna("").astype(str).values).lower()
            if search_mode.startswith("AND"):
                return all(k.lower() in row_str for k in keywords)
            else:
                return any(k.lower() in row_str for k in keywords)

        df_matched = df_raw[df_raw.apply(check_match, axis=1)].copy()
        
        if selected_dept != "전체 부서" and "부서명" in df_matched.columns:
            df_matched = df_matched[df_matched["부서명"] == selected_dept]

        matched_emp_count = df_matched["사번"].nunique()
        
        st.markdown(f"### 📋 매칭 결과 : 총 **{matched_emp_count}명** 검색됨")
        
        if matched_emp_count > 0:
            grouped = df_matched.groupby(["사번", "성명", "부서명"])
            
            for (emp_id, emp_name, dept_name), group_df in grouped:
                total_months = pd.to_numeric(group_df["투입개월수"], errors='coerce').sum()
                
                langs = group_df["Language"].dropna().unique().tolist() if "Language" in group_df.columns else []
                dbms = group_df["DBMS"].dropna().unique().tolist() if "DBMS" in group_df.columns else []
                fws = group_df["Framework"].dropna().unique().tolist() if "Framework" in group_df.columns else []
                
                skill_summary = f"**Language:** {', '.join(langs)} | **DBMS:** {', '.join(dbms)} | **Framework:** {', '.join(fws)}"
                
                with st.expander(f"👤 {emp_name} ({dept_name}) - 사번: {emp_id} | 매칭 경력 {len(group_df)}건 (총 {total_months:.0f}개월)"):
                    st.markdown(f"💡 **주요 기술스택:** {skill_summary}")
                    
                    display_cols = [c for c in ['회사명', '사업/직렬 명', '투입시작일자', '투입종료일자', '투입개월수', '업무 상세', 'IT직무명', 'Language', 'DBMS'] if c in group_df.columns]
                    st.dataframe(group_df[display_cols], use_container_width=True, hide_index=True)
        else:
            st.warning("⚠️ 입력하신 조건과 일치하는 대상자가 없습니다.")
    else:
        st.info("💡 상단에 기술(예: Java, Oracle) 또는 업무 키워드(예: 회계, SM)를 입력하면 적합 인재가 조회됩니다.")
        st.markdown("#### 📄 전체 데이터 미리보기 (상위 10건)")
        st.dataframe(df_raw.head(10), use_container_width=True, hide_index=True)