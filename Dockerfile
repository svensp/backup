FROM bitnami/minideb:buster

RUN apt-get update \
   && apt-get -y install \
      python3 \
      python3-pip \
      borgbackup \
      mariadb-backup \
   && pip3 install \
      paramiko-ng \
      pyAesCrypt \
      dependency-injector \
   && rm -Rf /var/lib/apt/lists/* \
   && mkdir -p /home/user

ENV PATH /opt/cloudbackup:$PATH
ENV HOME /home/user

COPY . /opt/cloudbackup

ENTRYPOINT [ "cloudbackup" ]
