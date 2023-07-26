FROM python:3.9-alpine

WORKDIR /app

RUN apk add python3-dev build-base linux-headers pcre-dev
COPY requirements.txt .

RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["uwsgi", "--ini", "uwsgi.ini"]
