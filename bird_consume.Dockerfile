FROM python:3-slim
WORKDIR /usr/src/app
COPY requirements.txt ./
RUN python -m pip install --no-cache-dir -r requirements.txt
COPY ./bird_consume.py ./invokes.py ./amqp_setup.py ./
CMD ["python", "./bird_consume.py"]