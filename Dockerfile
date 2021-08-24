# Using python debian
FROM python:3.9.6-buster

# http://bugs.python.org/issue19846
ENV LANG C.UTF-8
# we don't have an interactive xTerm
ENV DEBIAN_FRONTEND noninteractive

RUN apt-get -qq update -y && apt-get -qq upgrade -y
RUN apt-get -qq install -y \
    git \
    curl \
    wget \
    ffmpeg \
    opus-tools

# Git clone repository + root 
RUN git clone https://github.com/Codex51/Codex.git /usr/src/usercodex
WORKDIR /usr/src/usercodex
ENV PATH="/usr/src/usercodex/bin:$PATH"

# Install requirements
RUN pip3 install -U -r requirements.txt

RUN chmod a+x start
CMD ["./start"]
