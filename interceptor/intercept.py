import json
import os
import shutil
import sys

import pkg_resources
from satella.coding import silence_excs
from satella.files import write_to_file, read_in_file

from interceptor.config import load_config_for, Configuration
from interceptor.whereis import filter_whereis

INTERCEPTED = '-intercepted'
INTERCEPTOR_WRAPPER_STRING = 'from interceptor.config import load_config_for'


def intercept(tool_name: str) -> None:
    source_file = pkg_resources.resource_filename(__name__, 'templates/cmdline.py')
    try:
        load_config_for(tool_name, None)
    except KeyError:
        print('No configuration found for %s, creating a default one' % (tool_name,))
        shutil.copy(pkg_resources.resource_filename(__name__, 'templates/config'),
                    os.path.join('/etc/interceptor.d', tool_name))
    source = filter_whereis(sys.argv[1])
    target_intercepted = source + INTERCEPTED
    with silence_excs(UnicodeDecodeError), open(source, 'rb') as f_in:
        if is_intercepted(tool_name):
            print('Target is already intercepted. Aborting.')
            sys.exit(1)
    shutil.copy(source, target_intercepted)
    os.unlink(source)
    source_content = read_in_file(source_file, 'utf-8')
    source_content = source_content.format(EXECUTABLE=sys.executable,
                                           TOOLNAME=tool_name,
                                           LOCATION=target_intercepted,
                                           VERSION=pkg_resources.require('interceptor')[0].version)
    write_to_file(source, source_content, 'utf-8')
    os.chmod(source, 0o555)
    print('Successfully intercepted %s' % (tool_name,))


def is_intercepted(app_name: str) -> bool:
    path = filter_whereis(app_name)

    with silence_excs(UnicodeDecodeError), open(path, 'rb') as f_in:
        intercepted_real = f_in.read(512).decode('utf-8')
        return INTERCEPTOR_WRAPPER_STRING in intercepted_real


def unintercept(app_name: str) -> None:
    source = filter_whereis(app_name + INTERCEPTED)
    src_name = source[:-len(INTERCEPTED)]
    os.unlink(src_name)
    shutil.move(source, src_name)
    print('Successfully unintercepted %s' % (app_name,))
    print('Leaving the configuration in place')


def assert_intercepted(app_name: str) -> None:
    if not is_intercepted(app_name):
        print('%s is not intercepted' % (app_name,))
        sys.exit(1)


def banner():
    print('''Unrecognized command. Usage:
    * intercept foo - intercept foo
    * intercept undo foo - cancel intercepting foo
    * intercept configure foo - type in the configuration for foo in JSON format, end with Ctrl+D
    * intercept show foo - show the configuration for foo
    * intercept display foo - enable displaying what is launched on foo's startup
    * intercept hide foo - disable displaying what is launched on foo's startup
    * intercept edit foo - launch a nano/vi to edit it's configuration
    * intercept append foo ARG - add ARG to be appended to command line whenever foo is ran
    * intercept prepend foo ARG - add ARG to be prepended to command line whenever foo is ran
    * intercept disable foo ARG - add ARG to be eliminated from the command line whenever foo is ran
    * intercept replace foo ARG1 ARG2 - add ARG1 to be replaced with ARG2 whenever it is passed to foo
    * intercept notify foo - display a notification each time an argument action is taken
    * intercept unnotify foo - hide the notification each time an argument action is taken
    * intercept link foo bar - symlink bar's config file to that of foo
    * intercept copy foo bar - copy foo's configuration onto that of bar
    * intercept reset foo - reset foo's configuration (delete it and create a new one)
    * intercept check foo - validate foo's configuration and reformat it
''')


def run():
    if not os.path.exists('/etc/interceptor.d'):
        print('/etc/interceptor.d does not exist, creating...')
        os.mkdir('/etc/interceptor.d')

    if len(sys.argv) == 2:
        intercept(sys.argv[1])
    elif len(sys.argv) >= 3:
        op_name = sys.argv[1]
        app_name = sys.argv[2]
        if len(sys.argv) >= 4:
            target_name = sys.argv[3]

        if op_name == 'undo':
            assert_intercepted(app_name)
            unintercept(app_name)
        elif op_name == 'status':
            if is_intercepted(app_name):
                print('%s is intercepted' % (app_name,))
                cfg_path = os.path.join('/etc/interceptor.d', app_name)
                if os.path.islink(cfg_path):
                    tgt_link = os.readlink(cfg_path).split('/')[-1]
                    print('%s is scheduled to read configuration from %s' % (app_name, tgt_link))
                else:
                    print('%s has it\'s own configuration' % (app_name,))
            else:
                print('%s is NOT intercepted' % (app_name,))
        elif op_name == 'configure':
            assert_intercepted(app_name)
            data = sys.stdin.read()
            try:
                json.loads(data)
            except json.JSONDecoder:
                print('Configuration is invalid JSON')
                sys.exit(1)
            write_to_file(os.path.join('/etc/interceptor.d', app_name), data, 'utf-8')
            print('Configuration successfully written')
        elif op_name == 'show':
            assert_intercepted(app_name)
            config = read_in_file(os.path.join('/etc/interceptor.d', app_name), 'utf-8')
            print(config)
        elif op_name == 'edit':
            assert_intercepted(app_name)
            editor = filter_whereis('nano', abort_on_failure=False)
            if editor is None:
                editor = filter_whereis('vi')
            os.execv(editor, [editor, os.path.join('/etc/interceptor.d', app_name)])
        elif op_name in ('append', 'prepend', 'disable', 'replace', 'display', 'hide',
                         'notify', 'unnotify'):
            assert_intercepted(app_name)
            arg = target_name
            cfg = load_config_for(app_name, None)
            if op_name == 'append':
                cfg.args_to_append.append(arg)
            elif op_name == 'prepend':
                cfg.args_to_prepend.append(arg)
            elif op_name == 'disable':
                cfg.args_to_disable.append(arg)
            elif op_name == 'replace':
                cfg.args_to_replace.append([arg, sys.argv[4]])
            elif op_name == 'display':
                cfg.display_before_start = True
            elif op_name == 'hide':
                cfg.display_before_start = False
            elif op_name == 'notify':
                cfg.notify_about_actions = True
            elif op_name == 'unnotify':
                cfg.notify_about_actions = False
            cfg.save()
            print('Configuration changed')
        elif op_name == 'link':
            assert_intercepted(app_name)
            assert_intercepted(target_name)
            source = os.path.join('/etc/interceptor.d', app_name)
            target = os.path.join('/etc/interceptor.d', target_name)
            if os.path.islink(source) and '--force' not in sys.argv[4:]:
                print('Refusing to link, since %s is already a symlink!' % (app_name, ))
                sys.exit(1)
            with silence_excs(IOError):
                os.unlink(target)
            os.system('ln -s %s %s' % (source, target))
            print('Linked %s to read from %s''s config' % (target_name, app_name))
        elif op_name == 'copy':
            assert_intercepted(app_name)
            assert_intercepted(target_name)
            source = os.path.join('/etc/interceptor.d', app_name)
            target = os.path.join('/etc/interceptor.d', target_name)
            with silence_excs(IOError):
                os.unlink(target)
            shutil.copy(source, target)
            print('Copied %s to from %s''s config' % (target_name, app_name))
        elif op_name == 'reset':
            assert_intercepted(app_name)
            path = os.path.join('/etc/interceptor.d', app_name)
            if os.path.islink(path):
                target = os.readlink(path).split('/')[-1]
                print('%s config was a symlink to %s' % (app_name, target))
            os.unlink()
            cfg = Configuration()
            cfg.app_name = app_name
            cfg.save()
            print('Configuration reset')
        elif op_name == 'check':
            assert_intercepted(app_name)
            cfg = load_config_for(app_name, None)
            cfg.save()
            print('Configuration is valid')
        else:
            print('Unrecognized command %s' % (op_name,))
            banner()
            sys.exit(1)
    else:
        banner()
