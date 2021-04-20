import os
import shutil
import sys

import pkg_resources
from satella.files import write_to_file, read_in_file

from interceptor.config import load_config_for
from interceptor.whereis import filter_whereis


def intercept(tool_name: str) -> None:
    source_file = pkg_resources.resource_filename(__name__, 'templates/cmdline.py')
    try:
        load_config_for(tool_name)
    except KeyError:
        print('No configuration found for %s, creating a default one' % (tool_name, ))
        shutil.copy(pkg_resources.resource_filename(__name__, 'templates/config'),
                    os.path.join('/etc/interceptor.d', tool_name))
    source = filter_whereis(sys.argv[1])
    target_intercepted = source+'-intercepted'
    if os.path.exists(target_intercepted):
        print('Target already intercepted. Aborting.')
        sys.exit(1)
    shutil.copy(source, target_intercepted)
    os.unlink(source)
    source_content = read_in_file(source_file, 'utf-8')
    source_content = source_content.format(EXECUTABLE=sys.executable,
                                           TOOLNAME=tool_name,
                                           LOCATION=target_intercepted)
    write_to_file(source, source_content, 'utf-8')
    os.chmod(source, 0o555)
    print('Successfully intercepted %s' % (tool_name, ))


def unintercept(app_name: str) -> None:
    f_name = app_name + '-intercepted'
    source = filter_whereis(f_name)
    src_name = source[:-len('-intercepted')]
    os.unlink(src_name)
    shutil.copy(source, src_name)
    print('Successfully unintercepted %s' % (app_name, ))
    print('Leaving the configuration in place')


def run():

    if not os.path.exists('/etc/interceptor.d'):
        print('/etc/interceptor.d does not exist, creating...')
        os.mkdir('/etc/interceptor.d')

    if len(sys.argv) == 2:
        intercept(sys.argv[1])
    if len(sys.argv) == 3:
        if sys.argv[1] == 'undo':
            unintercept(sys.argv[2])
        else:
            print('''Unrecognized command. Usage:
* intercept foo - intercept foo
* intercept undo foo - cancel intercepting foo
''')
            sys.exit(1)
