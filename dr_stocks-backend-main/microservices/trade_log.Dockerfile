FROM python:3-slim
WORKDIR /usr/src/app
COPY requirements.txt ./
RUN python -m pip install --no-cache-dir -r requirements.txt
COPY ./trade_log.py ./amqp_setup.py ./
CMD [ "python", "./trade_log.py" ]