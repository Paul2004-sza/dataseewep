# wsgi.py
import sys
import os

# This path will be updated on PythonAnywhere
project_home = '/home/yourusername/StockMarketWebapp'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

os.chdir(project_home)

from run import app as application