FROM python:3.10.5-alpine

RUN apk add --no-cache git bash curl unzip
RUN curl https://rclone.org/install.sh | bash
RUN rclone config file

RUN git clone https://github.com/Alyetama/Force-Forward-Outlook.git
WORKDIR Force-Forward-Outlook
RUN pip3 install -r requirements.txt

ENTRYPOINT ["python3", "forwardgod.py"]
