docker rm -f kdjrest
docker run -d -p 5000:5000  \
            -v /dc/dckdj2:/code  \
            -i -t  \
            -e "TZ=Asia/Chongqing"  \
            --name kdjrest kdjrest:base  \
             /bin/bash
            # python rest/main.py
docker exec kdjrest python /code/rest/web.py


# docker rm -f kdjrest
# docker rmi -f kdjrest:server
# docker build -t kdjrest:server rest

# docker run -p 5000:5000 -it --name kdjrest kdjrest:server