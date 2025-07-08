FROM python:3.10-slim

WORKDIR /app

COPY . .

# Upgrade pip and install required packages
RUN python -m pip install --upgrade pip && \
    pip install fastapi wget pydantic uvicorn && \
    pip install -r requirements.txt

EXPOSE 8000

# Correct CMD syntax: each argument must be a separate string
CMD ["uvicorn", "slack_server:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]