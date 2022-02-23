FROM python:3.10

COPY ./telegram /telegram
COPY ./requirements.txt /

RUN pip install -r requirements.txt

CMD ["python3", "/telegram/main.py"]

