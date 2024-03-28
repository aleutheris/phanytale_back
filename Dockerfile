FROM python:3.10.6-slim

WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5001

CMD ["python", "main.py"]
