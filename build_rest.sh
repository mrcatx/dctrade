docker stop dcrest
docker rm -f dcrest
docker run -d -p 5000:5000  \
            -v /dc/dctrade:/code  \
            -i -t  \
            -e "TZ=Asia/Chongqing"  \
            --name dcrest kdjrest:base  \
             /bin/bash
            # python rest/main.py
docker exec dcrest python /code/rest/web.py


# docker rm -f kdjrest
# docker rmi -f kdjrest:server
# docker build -t kdjrest:server rest

# docker run -p 5000:5000 -it --name kdjrest kdjrest:server