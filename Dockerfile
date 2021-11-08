FROM mcr.microsoft.com/playwright:focal

RUN apt-get update && apt-get install -y python3-pip
COPY . .
RUN pip3 install TikTokApi
RUN python -m playwright install

RUN pip3 install flask
RUN pip3 install flask_cors

EXPOSE 5000
ENTRYPOINT [ "python3" ]
CMD [ "tiktokserver.py" ]