FROM debian:bullseye

RUN apt-get update \
   && apt-get -y install \
      python3 \
      python3-pip \
      borgbackup \
      mariadb-backup \
      openssh-client \
   && pip3 install \
      paramiko-ng \
      pyAesCrypt \
      dependency-injector \
      python-dateutil \
      prometheus_client \
   && rm -Rf /var/lib/apt/lists/* \
   && mkdir -p /home/user

RUN adduser user --uid 1000 --gid 1000

ENV PATH /opt/cloudbackup:$PATH
ENV HOME /home/user

COPY . /opt/cloudbackup

ENTRYPOINT [ "cloudbackup" ]
