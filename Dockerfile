# Python 3.11 slim 이미지를 사용
FROM python:3.11-slim

# 작업 디렉토리 생성 및 이동
WORKDIR /app

# 시스템 패키지 설치 (httpx 등 빌드 필요시 대비)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 소스 복사
COPY . /app

# 가상환경 생성 및 활성화, 의존성 설치
RUN python -m venv /opt/venv \
    && . /opt/venv/bin/activate \
    && pip install --upgrade pip \
    && pip install --no-cache-dir httpx

# FastMCP가 별도 패키지라면 requirements.txt에 추가 필요
# (예시) RUN pip install --no-cache-dir fastmcp

# 환경변수 설정 (실행 시 외부에서 주입)
ENV PATH="/opt/venv/bin:$PATH"

# 기본 실행 명령
CMD ["python", "main.py"] 