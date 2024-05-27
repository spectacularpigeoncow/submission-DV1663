FROM python:3.12

EXPOSE 5000

WORKDIR /app

COPY requirements.txt /app
RUN pip install -r requirements.txt

COPY app.py /app
COPY static /app/static
COPY templates /app/templates

CMD python app.py
