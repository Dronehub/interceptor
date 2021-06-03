import json
import os
import sys

from satella.files import write_to_file, read_in_file

from interceptor.intercepting import intercept_tool, unintercept_tool, assert_intercepted, check, \
    abort, link, assert_etc_interceptor_d_exists, edit, reset, configure


def banner():
    print('''Usage:
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
    * intercept log foo - enable logging to /var/log/interceptor.d for foo
    * intercept unlog foo - disable logging to /var/log/interceptor.d for foo
Use the optional switch --force is you need a command to complete despite the command telling you 
that it is impossible to complete. One trick: already intercepted files won't be intercepted, because
that would lead to overwriting of the original executable, so interceptor won't do that.
''')


def run():
    assert_etc_interceptor_d_exists()

    if len(sys.argv) == 2:
        intercept_tool(sys.argv[1])
    elif len(sys.argv) >= 3:
        op_name = sys.argv[1]
        app_name = sys.argv[2]
        target_name = sys.argv[3] if len(sys.argv) >= 4 else None

        if op_name == 'undo':
            unintercept_tool(app_name)
        elif op_name == 'configure':
            assert_intercepted(app_name)
            data = sys.stdin.read()
            try:
                json.loads(data)
            except json.JSONDecoder:
                print('Configuration is invalid JSON')
                abort()
            write_to_file(os.path.join('/etc/interceptor.d', app_name), data, 'utf-8')
            print('Configuration successfully written')
        elif op_name == 'show':
            assert_intercepted(app_name)
            config = read_in_file(os.path.join('/etc/interceptor.d', app_name), 'utf-8')
            print(config)
        elif op_name == 'status':
            check(app_name, add_config=False)
        elif op_name == 'edit':
            edit(app_name)
        elif op_name in ('append', 'prepend', 'disable', 'replace', 'display', 'hide',
                         'notify', 'unnotify', 'log', 'unlog'):
            configure(op_name, app_name, target_name)
        elif op_name == 'link':
            link(app_name, target_name)
        elif op_name == 'copy':
            link(app_name, target_name, copy=True)
        elif op_name == 'reset':
            reset(app_name)
        else:
            print('Unrecognized command %s' % (op_name,))
            banner()
            sys.exit(1)
    else:
        banner()
