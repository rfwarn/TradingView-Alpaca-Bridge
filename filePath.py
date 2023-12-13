import os

def filePath():
    # Get file path
    return os.path.dirname(__file__)

def fileName(fn):
    # Get file name
    return os.path.basename(fn)
    