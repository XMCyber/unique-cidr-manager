FROM python:alpine3.20

WORKDIR /app
COPY . .

RUN pip install -r requirements.txt
RUN apk add git

CMD ["python", "server/main.py"]
ENV PYTHONUNBUFFERED=1

EXPOSE 8000