FROM python:3.10-alpine

RUN apk add gcc python3-dev musl-dev


RUN apk add build-base
RUN apk add python3-tkinter


RUN pip3 install asyncpg 


COPY ./requirements.txt /
RUN pip install -r requirements.txt

COPY ./telegram /telegram

CMD ["python3", "/telegram/main.py"]

