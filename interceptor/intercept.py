import os
import shutil
import sys

import pkg_resources
from satella.files import write_to_file, read_in_file

from interceptor.config import load_config_for
from interceptor.whereis import filter_whereis

INTERCEPTED = '-intercepted'


def intercept(tool_name: str) -> None:
    source_file = pkg_resources.resource_filename(__name__, 'templates/cmdline.py')
    try:
        load_config_for(tool_name)
    except KeyError:
        print('No configuration found for %s, creating a default one' % (tool_name, ))
        shutil.copy(pkg_resources.resource_filename(__name__, 'templates/config'),
                    os.path.join('/etc/interceptor.d', tool_name))
    source = filter_whereis(sys.argv[1])
    target_intercepted = source+INTERCEPTED
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


def is_intercepted(app_name: str) -> bool:
    path = filter_whereis(app_name)
    return os.path.exists(path) and os.path.exists(path+INTERCEPTED) \
           and os.path.exists(os.path.join('/etc/interceptor.d', app_name))


def unintercept(app_name: str) -> None:
    source = filter_whereis(app_name + INTERCEPTED)
    src_name = source[:-len(INTERCEPTED)]
    os.unlink(src_name)
    shutil.move(source, src_name)
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
        elif sys.argv[1] == 'status':
            if is_intercepted(sys.argv[2]):
                print('%s is intercepted' % (sys.argv[2], ))
            else:
                print('%s is NOT intercepted' % (sys.argv[2], ))
        else:
            print('''Unrecognized command. Usage:
* intercept foo - intercept foo
* intercept undo foo - cancel intercepting foo
''')
            sys.exit(1)
