FROM python:3.8-slim

WORKDIR /app/

COPY configuration/ .

RUN pip3 install -r requirements.txt --no-cache-dir

CMD ["gunicorn", "configuration.wsgi:application", "--bind", "0:8000" ] 