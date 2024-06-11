FROM python:3.11-slim

COPY . /app

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    nano \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*


RUN pip install --upgrade pip
RUN pip install setuptools wheel

RUN pip install /app

RUN mkdir /data
WORKDIR /data
ENTRYPOINT ["streamlit", "run", "/app/gui/app.py"]
