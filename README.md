# 🏢 HR Management App

Streamlit 기반의 HR 업무 자동화 및 관리 지원 웹 애플리케이션입니다.  
사내 동호회 회원 검증 등 반복적인 HR 행정 업무를 효율화하기 위해 제작되었습니다.

---

## 🚀 주요 기능

- 🔍 동호회 유효회원 검증기 (`club_verification.py`)**
  - 제출된 은행 거래내역서 원본(.pdf) 업로드 및 자동 파싱
  - 회비 입금 내역 추출 및 월별 연속성 자동 진단
  - 원본 PDF 문서 대조 viewer 제공
  - 검증 결과 데이터 조회 및 CSV 추출 지원

---

## 🛠️ 기술 스택

- UI / Web: Python 3.10+, Streamlit
- Data Processing: Pandas, pdfplumber
- PDF Engine: pdf2image, Poppler

---

## 📦 설치 및 실행 방법

아래 명령어를 터미널에 순서대로 실행하세요.

```bash
# 1. Repository Clone 및 이동
git clone [https://github.com/moing9070-droid/hr-management-app.git](https://github.com/moing9070-droid/hr-management-app.git)
cd hr-management-app

# 2. 가상환경 세팅 및 패키지 설치 (Windows 기준)
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# 3. 앱 실행
streamlit run app.py
