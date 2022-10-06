FROM python:3-slim
WORKDIR /usr/src/app
COPY requirements.txt ./
RUN python -m pip install --no-cache-dir -r requirements.txt
COPY ./email_notification.py ./amqp_setup.py ./
CMD [ "python", "./email_notification.py" ]