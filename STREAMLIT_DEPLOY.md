# Streamlit Community Cloud 배포 (무료·카드 불필요)

DUOMO 쇼케이스 생성기를 인터넷 공개 URL로 띄워 팀이 접속하는 방법.

## 왜 Streamlit Cloud인가
- **무료, 카드 등록 불필요** (Anthropic 카드 막힘 우회)
- GitHub 레포 연결 → 자동 배포·자동 갱신
- **비공개 앱 + 이메일 허용목록** = 팀만 접속 (OAuth 셋업 불필요)
- Playwright는 `playwright==1.49.0` + `packages.txt` + 부팅시 `playwright install chromium`로 동작 (이미 코드에 반영됨)

## 사전 반영 완료 (코드)
- `packages.txt` — Chromium 시스템 라이브러리 (Streamlit Cloud가 apt로 설치)
- `render/bootstrap.py` + `app.py` — 첫 부팅 시 Chromium 1회 설치
- `requirements.txt` — `playwright==1.49.0` 고정 (Cloud 호환)
- GitHub 레포 푸시 완료 (egodomum/duomo-landing-tool, 비공개)

## 사용자가 할 일 (브라우저, 약 5분)

### 1. Streamlit Community Cloud 로그인
https://share.streamlit.io → **"Continue with GitHub"** (egodomum 계정)

### 2. 앱 생성
- **"Create app"** → **"Deploy a public app from GitHub"**
- Repository: `egodomum/duomo-landing-tool`
- Branch: `main`
- Main file path: `app.py`
- **Advanced settings → Python version: 3.11** (3.14는 일부 패키지 미지원 가능 — 3.11 권장)

### 3. Secrets 입력 (Advanced settings → Secrets)
TOML 형식으로 붙여넣기:
```toml
DEMO_MODE = "1"
GEMINI_API_KEY = "여기에_Gemini_키"
GEMINI_IMAGE_MODEL = "gemini-2.5-flash-image"
# ANTHROPIC_API_KEY = "sk-ant-..."   # 카피 자동생성 쓰려면. 없으면 카피는 수동 입력
```
> Streamlit Cloud는 secrets를 환경변수로도 주입하므로 `os.getenv`가 그대로 읽습니다.

### 4. Deploy 클릭
- 첫 빌드 5~10분 (Chromium 다운로드 포함)
- 완료되면 `https://<앱이름>.streamlit.app` URL 발급

### 5. 팀만 접속하게 (비공개 전환) ⚠️ 중요
배포 후 앱 설정 → **Settings → Sharing**:
- **"Who can view this app"** → **"Specific people"**
- 팀원 Google 이메일들 추가 (@duomonco.com 등)
- → 허용된 이메일만 접속, API 키 오남용 방지

(공개로 두면 누구나 접속해 Gemini 키를 소모할 수 있으니 반드시 비공개+허용목록.)

## 운영 메모
- 코드 수정 후 `git push` 하면 Streamlit Cloud가 자동 재배포
- 앱이 안 쓰이면 자동 sleep → 첫 접속 시 깨어남(수십 초)
- 렌더 결과 PNG는 컨테이너 임시 디렉터리에 생성 → 다운로드 버튼으로 받기
- ⚠️ Python 3.11 권장 (Cloud 기본). 3.14에서 일부 휠 미빌드 가능

## 대안 (참고)
- **Hugging Face Spaces (Docker)**: Playwright를 Dockerfile에 박아 더 안정적, 무료. 단 팀 비공개는 HF 계정 필요.
- **Google Cloud Run**: 가장 production급(Dockerfile 있음). 단 GCP 결제(카드) 필요.
