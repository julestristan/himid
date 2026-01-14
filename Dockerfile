FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
# Making sure packages are not outdated
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

CMD ["python","main.py"]