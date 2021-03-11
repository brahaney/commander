FROM python:3

COPY --from=docker:dind /usr/local/bin/docker /usr/local/bin/ 
RUN apt update && apt-get install -y docker-compose

COPY requirements.txt /tmp/requirements.txt

RUN pip install -r /tmp/requirements.txt

COPY src /app/commander

ENTRYPOINT [ "python", "/app/commander/commander.py" ]
