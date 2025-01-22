docker build -t ui_server -f docker/Dockerfile .
docker stop ui_server || true && docker rm ui_server || true
docker run -d -p 8003:8000 --restart unless-stopped --net consultant_ai --net monitoring  -v $(pwd):/app --name ui_server ui_server
