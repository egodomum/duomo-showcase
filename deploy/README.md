# Cloud Run 배포

## 사전 준비

1. **GCP 프로젝트 생성** (예: `duomo-internal`)
2. **API 활성화**:
   ```bash
   gcloud services enable run.googleapis.com \
       artifactregistry.googleapis.com \
       cloudbuild.googleapis.com \
       drive.googleapis.com
   ```
3. **Artifact Registry 리포 생성**:
   ```bash
   gcloud artifacts repositories create duomo \
       --repository-format=docker --location=asia-northeast3
   ```
4. **OAuth 2.0 클라이언트 생성** (GCP Console > APIs & Services > Credentials):
   - Authorized redirect URIs에 Cloud Run URL 추가 (예: `https://duomo-landing-tool-xxx.run.app`)
   - 동의 화면을 "Internal" (Workspace 한정)로 설정
5. **Secret 등록**:
   ```bash
   echo -n "sk-ant-..." | gcloud secrets create anthropic-key --data-file=-
   echo -n "GOCSPX-..." | gcloud secrets create oauth-secret --data-file=-
   ```
6. **Drive에 폴더·인덱스 파일 생성**:
   - `/duomo/lookbook/` 공유 폴더 → ID를 `DRIVE_LOOKBOOK_FOLDER_ID` 로
   - 폴더 안에 빈 `_index.json` (내용: `[]`) → ID를 `DRIVE_LOOKBOOK_INDEX_ID` 로
   - `/duomo/landing-output/` 공유 폴더 → ID를 `DRIVE_OUTPUT_FOLDER_ID` 로

## 배포

```bash
export PROJECT_ID=duomo-internal
export GOOGLE_OAUTH_CLIENT_ID=xxx.apps.googleusercontent.com
export GOOGLE_OAUTH_REDIRECT_URI=https://duomo-landing-tool-xxx.run.app
export ALLOWED_DOMAIN=duomo.co.kr
export DRIVE_LOOKBOOK_FOLDER_ID=...
export DRIVE_LOOKBOOK_INDEX_ID=...
export DRIVE_OUTPUT_FOLDER_ID=...

bash deploy/deploy.sh
```

## 첫 배포 후

1. Cloud Run URL을 OAuth 클라이언트의 redirect URI에 등록 (Console에서 수정)
2. 두 번째 배포로 redirect_uri 확정
