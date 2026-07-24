# 🏢 HR Management App

Streamlit 기반의 HR 업무 자동화 및 인재 관리 지원 웹 애플리케이션입니다.  
동호회 유효회원 검증, 직무 역량/경력 기반 인재 검색 등 반복적이고 복잡한 HR 행정·기획 업무를 자동화하고 효율화하기 위해 제작되었습니다.

---

## 🚀 주요 기능

### 1. 🔍 동호회 유효회원 검증기 (`pages/club_verification.py`)
- **자동 파싱 & 연속성 검증:** 은행 거래내역서 원본(.pdf) 업로드 시 회비 입금 내역을 자동 추출하여 2개월 연속 납부 여부를 원클릭 정밀 진단
- **원본 문서 실시간 대조:** 좌측 원본 PDF 스캔 이미지 뷰어와 우측 추출 데이터 Grid를 동시 제공하여 검증 정확도 향상
- **특정 대상자 추적 & 리포트 추출:** 개별 회원별 입금 이력 집중 추적 모드 및 검증 결과 CSV 다운로드 지원

### 2. 🎯 직무 역량/경력 매칭 - Talent Finder (`pages/talent_finder.py`)
- **키워드 기반 인재 검색:** 기술 스택(Language, DBMS, Framework 등) 및 업무 상세 경력 키워드 다중 검색(AND/OR)
- **부서 및 직무 필터링:** 부서별·직무별 필터링을 통한 사내 직무 순환 및 프로젝트 적합자 조회
- **프로필 카드 & 경력 요건 요약:** 직원별 총 투입 개월 수, 주요 기술 스택 요약 및 프로젝트 이력 카드형 UI 제공

---

## 🛠️ 기술 스택

- **UI / Web:** Python, Streamlit
- **Data Processing:** Pandas, OpenPyXL, pdfplumber
- **PDF & Image Engine:** pdf2image, Poppler

---

## ⚙️ OS별 필수 전처리 (Poppler 설정)

`pdf2image` 라이브러리를 통한 PDF 변환을 위해 OS 환경에 맞는 설정이 필요합니다.

- **Windows (로컬 개발 환경):**
  - 프로젝트 최상위 루트에 `poppler` 폴더(내부에 `bin` 또는 `Library/bin` 포함)를 위치시킵니다.
  - 앱이 자동으로 OS(Windows)를 감지하여 로컬 Poppler 경로를 연결합니다.
  *(※ 대용량 바이너리 파일이므로 Git 추적 제외 `.gitignore` 권장)*

- **Linux / Streamlit Cloud (배포 환경):**
  - 프로젝트 최상위 루트의 `packages.txt`에 OS 패키지를 명시하여 자동 설치됩니다.
  ```text
  poppler-utils

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
