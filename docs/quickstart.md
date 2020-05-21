# Quickstart

## Requirements
You will need the following:

- Docker installed on your machine
- Access to a Hetzner Storagebox

## Start

### Create the backup script to use
- Copy examples/docker-backup to /usr/local/bin and edit your access data into it
  - BORG\_PASSWORD: This password will be used to encrypt file backups. Can be
    generated at https://passwordsgenerator.net/
  - MYSQL\_ENC\_PASSWORD: This password will be used to encrypt mysql backups. Can be
    generated at https://passwordsgenerator.net/
  - HETZNER\_SSHKEY: Can be set to a specific id\_rsa file. Use 'agent' unless
    you have something special in mind
  - HETZNER\_USER: Storagebox User
  - HETZNER\_STORAGEBOX: Storagebox dns name
  - HETZNER\_HOSTKEY: SSH Hostkey of the storagebox. Can be retrieved with  
    `ssh-keyscan u123456.your-storagebox.de`  
    use only the line NOT starting with #

### Gain ssh key access
- make sure you have a rsa ssh private+public key pair in ~/.ssh/{id\_rsa,id\_rsa.pub}
  - If not generate one with ssh-keygen
- Execute `docker-backup storage:auth` this will copy your public key to the
  storagebox in both the regular and the rfc format - allowing you to connect to
  both port 22 and 23 on the storagebox with your ssh key  
  It will ask for the storagebox password to connect

### Create resort and initialize file and mysql backup
- `docker-backup resorts:create some-application` - creates the resort
  some-application
- `docker-backup mysql:create some-application` - enables mysql backups in the
  resort some-application
- `docker-backup mysql:create some-application` - enables file backups in the
  resort some-application
