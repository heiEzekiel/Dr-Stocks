FROM python:3-slim
WORKDIR /usr/src/app
COPY requirements.txt ./
RUN python -m pip install --no-cache-dir -r requirements.txt
COPY ./transaction_log.py ./amqp_setup.py ./
CMD [ "python", "./transaction_log.py" ]