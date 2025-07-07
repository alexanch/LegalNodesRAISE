FROM python:3.10-slim

WORKDIR /app

COPY . .
RUN python -m pip install fastapi wget pydantic
RUN python -m pip install -r ./requirements.txt

EXPOSE 8002

CMD ["python", "main_server.py"]