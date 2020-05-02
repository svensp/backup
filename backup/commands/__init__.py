from dependency_injector import containers
from dependency_injector import providers
from .storage_auth_command import StorageAuthCommand
from .resorts_list_command import ResortsListCommand
from .resorts_create_command import ResortsCreateCommand
from .resorts_remove_command import ResortsRemoveCommand
from .files_create_command import FilesCreateCommand

class CommandContainer(containers.DeclarativeContainer):
    storageAuth = providers.Factory(StorageAuthCommand)

    resortsList = providers.Factory(ResortsListCommand)
    resortsCreate = providers.Factory(ResortsCreateCommand)
    resortsRemove = providers.Factory(ResortsRemoveCommand)

    filesCreate = providers.Factory(FilesCreateCommand)
