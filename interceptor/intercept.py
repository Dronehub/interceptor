import os
import shutil
import sys

import pkg_resources
from satella.files import write_to_file

from interceptor.config import load_config_for
from interceptor.whereis import filter_whereis


def run():
    source_file = pkg_resources.resource_filename(__name__, 'templates/cmdline.py')

    if not os.path.exists('/etc/interceptor.d'):
        print('/etc/interceptor.d does not exist, creating...')
        os.mkdir('/etc/interceptor.d')

    tool_name = sys.argv[1]
    try:
        load_config_for(tool_name)
    except KeyError:
        print('No configuration found for %s, creating a default one' % (tool_name, ))
        write_to_file(os.path.join('/etc/interceptor.d', tool_name), b'{}')
    source = filter_whereis(sys.argv[1])
    shutil.copy(source, source+'-intercepted')
    os.unlink(source)
    shutil.copy(source_file, source)
    os.chmod(source, 0o555)
    print('Successfully intercepted %s' % (tool_name, ))
