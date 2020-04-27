from dependency_injector import containers
from dependency_injector import providers
from .resorts_command import ResortsCommand

class CommandContainer(containers.DeclarativeContainer):
    resorts = providers.Factory(ResortsCommand)
