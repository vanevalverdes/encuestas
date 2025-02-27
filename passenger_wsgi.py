import sys, os

INTERP = "/home/encuestas25opol/public_html/application/venv/bin/python"
if sys.executable != INTERP: os.execl(INTERP, INTERP, *sys.argv)

from index import app as application
