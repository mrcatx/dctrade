docker run -d -p 12010:12010  \
            -v /dc/dctrade:/code  \
            -i -t  \
            -e "TZ=Asia/Chongqing"  \
            --name dckdj2 continuumio/anaconda3  \
             /bin/bash

