FROM python:3.9.7

ENV HOME /root

WORKDIR /app


COPY requirements.txt ./

RUN pip3 install --no-cache-dir -r requirements.txt

COPY app/. .

EXPOSE 8000

ADD https://github.com/ufoscout/docker-compose-wait/releases/download/2.2.1/wait /wait
RUN chmod +x /wait

CMD /wait && python3 app.py

