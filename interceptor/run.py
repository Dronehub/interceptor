import json
import os
import shutil
import sys

from satella.coding import silence_excs
from satella.files import write_to_file, read_in_file

from interceptor.config import load_config_for, Configuration
from interceptor.intercepting import intercept_tool, unintercept_tool, assert_intercepted, check
from interceptor.whereis import filter_whereis


def banner():
    print('''Unrecognized command. Usage:
    * intercept foo - intercept foo
    * intercept undo foo - cancel intercepting foo
    * intercept configure foo - type in the configuration for foo in JSON format, end with Ctrl+D
    * intercept show foo - show the configuration for foo
    * intercept status foo - display foo's status of interception and details about it's configuration
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
    
Use the optional switch --force is you need a command to complete despite the command telling you 
that it is impossible to complete. One trick: already intercepted files won't be intercepted, because
that would lead to overwriting of the original executable, so interceptor won't do that.
''')


def run():
    if not os.path.exists('/etc/interceptor.d'):
        print('/etc/interceptor.d does not exist, creating...')
        os.mkdir('/etc/interceptor.d')

    if len(sys.argv) == 2:
        intercept_tool(sys.argv[1])
    elif len(sys.argv) >= 3:
        op_name = sys.argv[1]
        app_name = sys.argv[2]
        if len(sys.argv) >= 4:
            target_name = sys.argv[3]

        if op_name == 'undo':
            unintercept_tool(app_name)
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
        elif op_name == 'status':
            check(app_name)
        elif op_name == 'edit':
            assert_intercepted(app_name)
            editor = filter_whereis('nano', abort_on_failure=False)
            if editor is None:
                editor = filter_whereis('vi')
            os.execv(editor, [editor, os.path.join('/etc/interceptor.d', app_name)])
        elif op_name in ('append', 'prepend', 'disable', 'replace', 'display', 'hide',
                         'notify', 'unnotify'):
            assert_intercepted(app_name)
            cfg = load_config_for(app_name, None)
            if op_name == 'append':
                cfg.arg_names_to_append.append(target_name)
            elif op_name == 'prepend':
                cfg.arg_names_to_prepend.append(target_name)
            elif op_name == 'disable':
                cfg.arg_names_to_disable.append(target_name)
            elif op_name == 'replace':
                cfg.arg_names_to_replace.append([target_name, sys.target_namev[4]])
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
            Configuration(app_name=app_name).save()
            print('Configuration reset')
        else:
            print('Unrecognized command %s' % (op_name,))
            banner()
            sys.exit(1)
    else:
        banner()
