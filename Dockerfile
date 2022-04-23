FROM python:3.10

COPY ./requirements.txt /
RUN pip install -r requirements.txt

COPY ./telegram /telegram

CMD ["python3", "/telegram/main.py"]

