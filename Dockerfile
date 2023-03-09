FROM python:3.10-alpine

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir 'fastapi[all]'

COPY . .

EXPOSE 8000

CMD [ "python", "-m", "uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000" ]
