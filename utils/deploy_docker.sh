docker build --file docker/Dockerfile -t ui_server .
docker container stop ui_server && docker container ui_server
docker run -d --name ui_server -e TZ=Asia/Tashkent -v $(pwd)/src/server.py:/app/src/server.py -v $(pwd)/configs:/app/src/configs ui_server