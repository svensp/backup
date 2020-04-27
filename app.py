#!/usr/bin/env python3
import sys
import backup.program

backup = backup.program.Program()
ret = backup.run()
sys.exit(ret)
