from dependency_injector import containers
from dependency_injector import providers
from .resorts_list_command import ResortsListCommand
from .resorts_create_command import ResortsCreateCommand
from .resorts_remove_command import ResortsRemoveCommand

class CommandContainer(containers.DeclarativeContainer):
    resortsList = providers.Factory(ResortsListCommand)
    resortsCreate = providers.Factory(ResortsCreateCommand)
    resortsRemove = providers.Factory(ResortsRemoveCommand)
