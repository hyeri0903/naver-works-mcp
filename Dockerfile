# Python 3.11 slim 이미지를 사용
FROM python:3.11-slim

# 작업 디렉토리 생성 및 이동
WORKDIR /app

# 시스템 패키지 설치 (httpx 등 빌드 필요시 대비)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# requirements.txt를 먼저 복사하여 Docker 레이어 캐싱 최적화
COPY requirements.txt .

# 가상환경 생성 및 활성화, 의존성 설치
RUN python -m venv /opt/venv \
    && . /opt/venv/bin/activate \
    && pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# 환경변수 설정
ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH="/app"

# 소스 코드 복사 (requirements.txt 설치 후)
COPY . /app

# MCP server용 사용자 생성 (보안 강화)
RUN useradd --create-home --shell /bin/bash mcp
RUN chown -R mcp:mcp /app /opt/venv
USER mcp

# stdio 통신을 위한 기본 실행 명령
CMD ["python", "main.py"]