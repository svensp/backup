# backup
Manage Backups on a Hetzner Storagebox

## Concept
Setting up backups has always been a pain even when you did it once per server
and everything on it magically got backed up by the existing scripts.

In a cloud environment you want as little single points of failure as possible -
so generally each app has its own mysql database server and files. However that
means you also need to 
