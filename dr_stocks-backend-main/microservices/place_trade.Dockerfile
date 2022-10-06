FROM python:3-slim
WORKDIR /usr/src/app
COPY requirements.txt ./
RUN python -m pip install --no-cache-dir -r requirements.txt
COPY ./place_trade.py ./invokes.py ./amqp_setup.py ./
CMD [ "python", "./place_trade.py" ]