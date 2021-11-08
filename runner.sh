docker build . -t tiktokapi:latest

docker run -d --rm -p 5000:5000 tiktokapi:latest