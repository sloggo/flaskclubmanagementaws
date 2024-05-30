FROM python:3.9-slim

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir --upgrade pip setuptools && \
    pip install --no-cache-dir -r requirements.txt

EXPOSE 80

ENV FLASK_APP=app.py

ARG DEPLOYMENT_TYPE=production

ENV FLASK_ENV=${DEPLOYMENT_TYPE}

CMD if [ "$FLASK_ENV" = "production" ]; then \
        flask run --host=0.0.0.0 --port=80; \
    else \
        flask run --host=0.0.0.0 --port=80 --reload --debugger; \
    fi
