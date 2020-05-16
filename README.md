# backup
Manage Backups on a Hetzner Storagebox

## Concept
Setting up backups has always been a pain even when you did it once per server
and everything on it magically got backed up by the existing scripts.

In a cloud environment you want as little single points of failure as possible -
so generally each app has its own mysql database server and files. However that
means you also need to reinvent the backup wheel for every service and generally
at least twice - one for the general files of an app and one for its database
system.

This script does not try to replace existing backup solutions but instead enrich
them:
- abstract the storage interface so it can be used against sftp or s3(reference
  implementation is for the hetzner storage box)
- Provide access to all backups from a single place
- make it easy to add another repository for another app

## Used backup software

### Mariabackup
Mariabackup is a fork of perconas xtrabackup patched to work with mariadb. It
uses a genius combination of copying the actual files from the filesystem and
reading the incoming changes to them through the binary log to create lightning
fast backups - as long as you're using the InnoDB storage engine.

### Borgbackup
