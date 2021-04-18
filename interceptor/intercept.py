import os
import shutil
import sys

import pkg_resources

from interceptor.config import load_config_for
from interceptor.whereis import filter_whereis


def run():
    source_file = pkg_resources.resource_filename(__name__, 'templates/cmdline.py')

    tool_name = sys.argv[1]
    try:
        load_config_for(tool_name)
    except KeyError:
        print('No configuration found for %s' % (tool_name, ))
        sys.exit(1)
    source = filter_whereis(sys.argv[1])
    shutil.copy(source, source+'-intercepted')
    os.unlink(source)
    shutil.copy(source_file, source)
    print('Successfully intercepted %s' % (tool_name, ))
