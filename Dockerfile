FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 5000
ENV DOCKER_BASE_URL=unix:///var/run/docker.sock
ENV APP_PORT=5000
ENV ADMIN_USER=admin
ENV ADMIN_PASS=admin123
CMD ["sh", "-c", "python app.py --port $APP_PORT --docker-url $DOCKER_BASE_URL"]