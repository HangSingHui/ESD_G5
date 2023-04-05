FROM python:3-slim
WORKDIR /usr/src/app
COPY requirements.txt ./
RUN python -m pip install --no-cache-dir -r requirements.txt
COPY ./accept_app.py ./invokes.py ./amqp_setup.py ./
CMD [ "python", "./accept_app.py" ]