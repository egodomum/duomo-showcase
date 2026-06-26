FROM python:3.11-slim

WORKDIR /app

# 시스템 의존성 (Pillow에 필요한 라이브러리)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libjpeg-dev \
    zlib1g-dev \
    libfreetype6-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py ./
COPY pages/ ./pages/
COPY pipeline/ ./pipeline/
COPY storage/ ./storage/
COPY auth/ ./auth/
COPY prompts/ ./prompts/
COPY design_tokens/ ./design_tokens/
COPY fonts/ ./fonts/

ENV PORT=8501
ENV PYTHONUNBUFFERED=1

EXPOSE 8501

CMD ["streamlit", "run", "app.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0", \
     "--server.headless=true", \
     "--browser.gatherUsageStats=false"]
