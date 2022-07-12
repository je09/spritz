FROM python:3.9
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY . /app/
WORKDIR /app
RUN pip install -r requirements.txt
EXPOSE 8000
RUN python manage.py makemigrations && \
    python manage.py migrate

CMD gunicorn spritz-backend.wsgi --bind 0.0.0.0:8000