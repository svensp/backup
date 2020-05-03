from dependency_injector import containers
from dependency_injector import providers
from .storage_auth_command import StorageAuthCommand
from .resorts_list_command import ResortsListCommand
from .resorts_create_command import ResortsCreateCommand
from .resorts_remove_command import ResortsRemoveCommand
from .files_create_command import FilesCreateCommand
from .files_backup_command import FilesBackupCommand
from .files_list_command import FilesListCommand
from .files_mount_command import FilesMountCommand
from .files_umount_command import FilesUmountCommand

class CommandContainer(containers.DeclarativeContainer):
    storageAuth = providers.Factory(StorageAuthCommand)

    resortsList = providers.Factory(ResortsListCommand)
    resortsCreate = providers.Factory(ResortsCreateCommand)
    resortsRemove = providers.Factory(ResortsRemoveCommand)

    filesCreate = providers.Factory(FilesCreateCommand)
    filesBackup = providers.Factory(FilesBackupCommand)
    filesList = providers.Factory(FilesListCommand)
    filesMount = providers.Factory(FilesMountCommand)
    filesUmount = providers.Factory(FilesUmountCommand)
