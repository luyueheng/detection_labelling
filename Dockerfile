FROM ubuntu:18.04

RUN apt update \
  && apt install -y python3.8 curl python3.8-distutils\
  && cd /usr/local/bin \
  && ln -s /usr/bin/python3.8 python

RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py \
  && python get-pip.py \
  && rm get-pip.py

RUN pip install Flask \ 
  && pip install PyMySQL

CMD /bin/bash
