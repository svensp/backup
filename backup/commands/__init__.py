from dependency_injector import containers
from dependency_injector import providers
from .storage_auth_command import StorageAuthCommand
from .storage_generate_key_command import StorageGenerateKeyCommand
from .resorts_list_command import ResortsListCommand
from .resorts_create_command import ResortsCreateCommand
from .resorts_remove_command import ResortsRemoveCommand
from .prometheus_metrics_command import PrometheusMetricsCommand
from .files_create_command import FilesCreateCommand
from .files_populate_command import FilesPopulateCommand
from .files_backup_command import FilesBackupCommand
from .files_remove_command import FilesRemoveCommand
from .files_list_command import FilesListCommand
from .files_mount_command import FilesMountCommand
from .files_umount_command import FilesUmountCommand
from .files_prune_command import FilesPruneCommand
from .mysql_create_command import MysqlCreateCommand
from .mysql_list_command import MysqlListCommand
from .mysql_backup_command import MysqlBackupCommand
from .mysql_restore_command import MysqlRestoreCommand
from .mysql_history_command import MysqlHistoryCommand
from .mysql_prune_command import MysqlPruneCommand

class CommandContainer(containers.DeclarativeContainer):
    storageAuth = providers.Factory(StorageAuthCommand)
    storageGenerateKey = providers.Factory(StorageGenerateKeyCommand)

    prometheusMetrics = providers.Factory(PrometheusMetricsCommand)

    resortsList = providers.Factory(ResortsListCommand)
    resortsCreate = providers.Factory(ResortsCreateCommand)
    resortsRemove = providers.Factory(ResortsRemoveCommand)

    filesCreate = providers.Factory(FilesCreateCommand)
    filesPopulate = providers.Factory(FilesPopulateCommand)
    filesBackup = providers.Factory(FilesBackupCommand)
    filesRemove = providers.Factory(FilesRemoveCommand)
    filesList = providers.Factory(FilesListCommand)
    filesMount = providers.Factory(FilesMountCommand)
    filesUmount = providers.Factory(FilesUmountCommand)
    filesPrune = providers.Factory(FilesPruneCommand)

    mysqlCreate = providers.Factory(MysqlCreateCommand)
    mysqlList = providers.Factory(MysqlListCommand)
    mysqlBackup = providers.Factory(MysqlBackupCommand)
    mysqlRestore = providers.Factory(MysqlRestoreCommand)
    mysqlHistory = providers.Factory(MysqlHistoryCommand)
    mysqlPrune = providers.Factory(MysqlPruneCommand)
