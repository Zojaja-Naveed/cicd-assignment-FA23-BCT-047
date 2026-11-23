
FROM python:3.12-slim-bookworm

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER=/usr/bin/chromedriver

RUN pip install --no-cache-dir selenium pytest

COPY test_site.py /app/test_site.py

RUN mkdir -p /app/screenshots /app/test-results

CMD ["pytest", "-v", "test_site.py", "--junitxml=/app/test-results/results.xml"]
