FROM python:3.12-slim
WORKDIR /app
RUN mkdir -p /data
COPY packages/ /tmp/packages/
RUN pip install --no-index --find-links=/tmp/packages flask docker
COPY dashboard/ .
EXPOSE 8000
CMD ["python", "app.py"]
