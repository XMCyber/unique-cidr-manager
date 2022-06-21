FROM python:alpine3.16

WORKDIR app
COPY . .

RUN pip install -r requirements.txt
RUN apk add git

CMD python server/main.py

EXPOSE 8000