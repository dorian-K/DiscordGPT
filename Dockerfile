FROM python:3.10-bullseye

RUN mkdir /bot
WORKDIR /bot
COPY requirements.txt /bot
RUN pip install -r requirements.txt
COPY .env /bot/
COPY main.py /bot/
ENTRYPOINT python main.py