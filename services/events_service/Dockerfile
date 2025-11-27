FROM python:3.10-slim

WORKDIR /app

RUN pip install --no-cache-dir \
    "Django>=4.2,<5.0" \
    "djangorestframework>=3.14,<4.0" \
    "pika>=1.3.0" \
    "requests>=2.31"

COPY . .

EXPOSE 8000
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

CMD ["/entrypoint.sh"]
