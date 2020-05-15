import argparse
import sys
from .command import Command
from datetime import datetime

class MysqlPruneCommand(Command):
    def __init__(self):
        self._name = "mysql:prune"
        self._description( 'Delete mysql backups following given rules')

    def setMySQL(self, mysql):
        self._mysql = mysql
        return self

    def run(self, parameters):
        args = self.__parseArgs(parameters)

        resortName = args.resortName
        resort = self._storage.findResort(resortName)
        resort.passAdapters(self)

        rules = args.rules

        print("Pruning backups")
        self._mysql.dryRun(args.dry_run).pruneBackups(rules)
        print("Pruned backups")
        return 0

    def __parseArgs(self, parameters):
        parser = argparse.ArgumentParser()
        parser.add_argument('resortName',
                help='The resort in which to create the backup')
        parser.add_argument('rules',
                nargs='+',
                help='Rules in the form tagname:allowed-age')
        parser.add_argument('--dry-run',
                action='store_true',
                help='If given check and print which backups are to be deleted but do not perform the deletion')
        return parser.parse_args(parameters)
