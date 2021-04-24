import logging
import os

from satella.exceptions import ProcessFailed
from satella.processes import call_and_return_stdout
import sys
import typing as tp

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


# unceremoniously taken from
# https://codereview.stackexchange.com/questions/190886/platform-independent-whereis-function
# and modified to better suit UNIX platforms
def whereis(app: str) -> tp.List[str]:
    result = None
    try:
        args = ['whereis', app]
        result = call_and_return_stdout(args,
                                        expected_return_code=0,
                                        encoding='utf-8')
    except ProcessFailed:
        print('whereis not found, aborting')
        sys.exit(1)

    if result is None:
        return []
    else:
        result = result.replace("\r", "").split("\n")
        results = []
        for line in result:
            line = line.strip()
            if not line:
                continue

            if ':' in line:
                results = line.split(':', 1)[1].strip().split(' ')
        return results


def filter_whereis(app: str, abort_on_failure=True) -> tp.Optional[str]:
    """
    Return a position of an executable. Verify that it's executable.
    """
    for path in whereis(app):
        if os.access(path, os.X_OK):
            yield path
    else:
        if not abort_on_failure:
            return
        else:
            print('%s not found, aborting' % (app,))
            sys.exit(1)
