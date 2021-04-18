import os, subprocess
import sys
from subprocess import CalledProcessError
import typing as tp

# unceremoniously taken from https://codereview.stackexchange.com/questions/190886/platform-independent-whereis-function
# and modified to better suit UNIX platforms
def whereis(app: str) -> tp.List[str]:
    try:
        result = subprocess.check_output(["whereis", app])

    except CalledProcessError:
        print('whereis not found, aborting')
        sys.exit(1)

    if result is None:
        return []
    else:
        result = result.decode().replace("\r", "").split("\n")
        result = list(filter(lambda x: len(x), result))
        return result


def filter_whereis(app: str) -> str:
    """
    Return a position of an executable. Verify that it's executable.
    """
    for path in whereis(app):
        if os.access(path, os. X_OK):
            return path

