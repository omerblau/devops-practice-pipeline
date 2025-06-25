FROM python:3.13.5-slim-bookworm

WORKDIR /app

COPY app.py .
COPY requirements.txt .

RUN apt update && apt install curl -y
RUN pip install -r requirements.txt

CMD  ["python", "app.py"]