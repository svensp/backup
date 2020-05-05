FROM bitnami/minideb:buster

RUN apt-get update \
   && apt-get -y install \
      python3 \
      python3-pip \
      borgbackup \
   && pip3 install paramiko-ng \
   && rm -Rf /var/lib/apt/lists/*

ENV PATH /opt/cloudbackup:$PATH

COPY . /opt/cloudbackup

ENTRYPOINT /opt/cloudbackup/cloudbackup
