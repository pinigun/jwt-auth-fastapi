FROM python:3.12.11-slim-bullseye


COPY ./src /app/src
COPY requirements.txt /app
COPY alembic.ini /app
COPY settings.py /app
COPY entrypoint.sh /app

WORKDIR /app
RUN pip install -r requirements.txt
RUN chmod +x entrypoint.sh
CMD ["bash", "-c", "./entrypoint.sh"]
