import logging
import os

from satella.os import whereis
import sys
import typing as tp

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


def filter_whereis(app: str, abort_on_failure=True) -> tp.Iterator[str]:
    """
    Return a position of an executable. Verify that it's executable.
    """
    found = False
    for path in whereis(app):
        if os.path.isdir(path):
            continue
        found = True
        yield path

    if not found:
        if not abort_on_failure:
            return
        else:
            print('%s not found, aborting' % (app,))
            sys.exit(1)
