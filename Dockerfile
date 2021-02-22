FROM python:3.9-slim

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

RUN useradd -ms /bin/bash worker
USER worker
WORKDIR /home/worker

ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

EXPOSE 5000
COPY --chown=worker:worker . .
#CMD ["flask", "run"]
