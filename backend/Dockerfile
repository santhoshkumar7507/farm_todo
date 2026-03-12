FROM python:3.12-slim

WORKDIR /usr/src/app

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    iputils-ping \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./

RUN pip install --no-cache-dir --upgrade -r ./requirements.txt

ENV SSL_CERT_FILE=/usr/local/lib/python3.12/site-packages/certifi/cacert.pem
ENV PYTHONUNBUFFERED=1

EXPOSE 3001

CMD ["uvicorn", "src.server:app", "--host", "0.0.0.0", "--port", "3001"]