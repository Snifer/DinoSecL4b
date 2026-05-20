FROM python:3.12-slim
WORKDIR /app
COPY packages/ /tmp/packages/
RUN pip install --no-index --find-links=/tmp/packages flask
COPY labs/a10-exceptional-conditions/app/ .
EXPOSE 5000
CMD ["python", "app.py"]
