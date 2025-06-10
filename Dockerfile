FROM python:3.9-slim

# Install Firefox dan dependensinya
RUN apt-get update && apt-get install -y \
    firefox-esr \
    wget \
    curl \
    libx11-xcb1 \
    libgdk-pixbuf2.0-0 \
    libxtst6 \
    libnss3 \
    && rm -rf /var/lib/apt/lists/*

# Install Geckodriver (Firefox WebDriver)
RUN curl -sSL https://github.com/mozilla/geckodriver/releases/download/v0.30.0/geckodriver-v0.30.0-linux64.tar.gz -o geckodriver.tar.gz \
    && tar -xvzf geckodriver.tar.gz \
    && mv geckodriver /usr/local/bin/

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app


# Perintah untuk menjalankan script Python Anda
CMD ["python3", "scraping-script.py"]
