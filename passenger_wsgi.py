import sys, os

INTERP = "/home/k4luzun1cocms/public_html/venv/bin/python"
if sys.executable != INTERP: os.execl(INTERP, INTERP, *sys.argv)

from index import app as application