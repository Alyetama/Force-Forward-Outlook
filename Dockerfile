FROM python:3.10.5-alpine

RUN apk add --no-cache bash curl unzip
RUN curl https://rclone.org/install.sh | bash && \
  rclone config file

WORKDIR /app

COPY forwardgod.py requirements.txt /app/

RUN pip3 install -r requirements.txt

ENTRYPOINT ["python3", "forwardgod.py"]
