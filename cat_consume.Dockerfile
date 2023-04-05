FROM python:3-slim
WORKDIR /usr/src/app
COPY requirements.txt ./
RUN python -m pip install --no-cache-dir -r requirements.txt
COPY ./cat_consume.py ./invokes.py ./amqp_setup.py ./
CMD ["python", "./cat_consume.py"]