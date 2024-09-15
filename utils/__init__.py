import subprocess
import os


# ----------------------------------------------------------------------
def start_service(destination):
    """"""
    subprocess.Popen(['python3', os.path.join(destination, 'main.py')])
