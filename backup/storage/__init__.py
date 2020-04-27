from dependency_injector import containers
from dependency_injector import providers
from .hetzner import HetznerStorage

class Container(containers.DeclarativeContainer):
    hetzner = providers.Factory()
