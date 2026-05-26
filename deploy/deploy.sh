#!/usr/bin/env bash
set -euo pipefail

# 사전 조건:
# - gcloud CLI 설치 + auth login 완료
# - GCP 프로젝트에 Cloud Run, Artifact Registry, Drive API 활성화
# - 환경변수 설정: PROJECT_ID, REGION (기본 asia-northeast3)

PROJECT_ID="${PROJECT_ID:?Set PROJECT_ID env var}"
REGION="${REGION:-asia-northeast3}"
SERVICE="duomo-landing-tool"
IMAGE="$REGION-docker.pkg.dev/$PROJECT_ID/duomo/$SERVICE:$(git rev-parse --short HEAD)"

echo "Building image: $IMAGE"
gcloud builds submit --tag "$IMAGE" --project "$PROJECT_ID"

echo "Deploying to Cloud Run..."
gcloud run deploy "$SERVICE" \
    --image "$IMAGE" \
    --region "$REGION" \
    --project "$PROJECT_ID" \
    --platform managed \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 1 \
    --min-instances 0 \
    --max-instances 3 \
    --timeout 3600 \
    --set-secrets="ANTHROPIC_API_KEY=anthropic-key:latest,GOOGLE_OAUTH_CLIENT_SECRET=oauth-secret:latest" \
    --set-env-vars="GOOGLE_OAUTH_CLIENT_ID=$GOOGLE_OAUTH_CLIENT_ID,GOOGLE_OAUTH_REDIRECT_URI=$GOOGLE_OAUTH_REDIRECT_URI,ALLOWED_DOMAIN=$ALLOWED_DOMAIN,DRIVE_LOOKBOOK_FOLDER_ID=$DRIVE_LOOKBOOK_FOLDER_ID,DRIVE_LOOKBOOK_INDEX_ID=$DRIVE_LOOKBOOK_INDEX_ID,DRIVE_OUTPUT_FOLDER_ID=$DRIVE_OUTPUT_FOLDER_ID"

echo "Done. URL:"
gcloud run services describe "$SERVICE" --region "$REGION" --project "$PROJECT_ID" \
    --format='value(status.url)'
