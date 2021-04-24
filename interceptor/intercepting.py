#
# Take care, in importing this module sys.argv gets changed!
#
import os
import shutil
import sys

import pkg_resources
from satella.coding import silence_excs
from satella.files import read_in_file, write_to_file

from interceptor.config import load_config_for, Configuration
from interceptor.whereis import filter_whereis

INTERCEPTED = '-intercepted'
INTERCEPTOR_WRAPPER_STRING = 'from interceptor.config import load_config_for'

FORCE = '--force' in sys.argv
if FORCE:
    sys.argv.remove('--force')


def is_intercepted(path_name: str, print_messages=False) -> bool:
    a = False
    with silence_excs(UnicodeDecodeError), open(path_name, 'rb') as f_in:
        intercepted_real = f_in.read(512).decode('utf-8')
        a = INTERCEPTOR_WRAPPER_STRING in intercepted_real

    if a:
        b = os.path.exists(path_name + INTERCEPTED)
        if not b:
            if print_messages:
                print('%s does not exist' % (path_name+INTERCEPTED, ))
            return b
    else:
        if print_messages:
            print('%s does not contain interceptor code' % (path_name, ))
    return False


def is_all_intercepted(name: str) -> bool:
    for path in filter_whereis(name):
        if not is_intercepted(path):
            return False
    return True


def assert_intercepted(name: str) -> None:
    if FORCE:
        print('Skipping a check to see if %s is intercepted due to --force' % (name, ))
        return
    if is_all_intercepted(name):
        return
    if is_partially_intercepted(name):
        print('''%s is partially intercepted. This means that there exist binaries of %s
'that have not been intercepted. To fix that, call:

intercept %s --force
''' % (name, name, name))
        return
    print('%s is not intercepted' % (name,))
    abort()


def is_partially_intercepted(name: str, print_messages=False) -> bool:
    interceptions = []
    for path in filter_whereis(name):
        if is_intercepted(path, print_messages=print_messages):
            if print_messages:
                print('%s is currently intercepted' % (path,))
            interceptions.append(True)
        else:
            interceptions.append(False)
    return not all(interceptions) and any(interceptions)


def is_completely_unintercepted(name: str) -> bool:
    return not is_all_intercepted(name) and not is_partially_intercepted(name)


def can_be_unintercepted(name: str) -> bool:
    for path in filter_whereis(name):
        if not is_intercepted(path):
            print('%s is not intercepted' % (path,))
            return False
        target_path = path + INTERCEPTED
        if not os.path.exists(target_path):
            print('%s does not exist' % (path,))
            return False
    return True


def abort():
    print('Aborting.')
    sys.exit(1)


def unintercept_path(path_name: str) -> None:
    src_name = path_name + INTERCEPTED
    shutil.move(src_name, path_name)
    print('Successfully unintercepted %s' % (path_name,))


def intercept_path(tool_name: str, file_name: str) -> None:
    source_file = pkg_resources.resource_filename(__name__, 'templates/cmdline.py')
    target_intercepted = file_name + INTERCEPTED
    previous_chmod = os.stat(file_name).st_mode & 0o777
    shutil.copy(file_name, target_intercepted)
    os.unlink(file_name)
    source_content = read_in_file(source_file, 'utf-8')
    source_content = source_content.format(EXECUTABLE=sys.executable,
                                           TOOLNAME=tool_name,
                                           LOCATION=target_intercepted,
                                           VERSION=pkg_resources.require('interceptor')[0].version)
    write_to_file(file_name, source_content, 'utf-8')
    os.chmod(file_name, previous_chmod)
    print('Successfully intercepted %s' % (file_name,))


def intercept_tool(tool_name: str):
    if is_partially_intercepted(tool_name):
        if not FORCE:
            print(
                '%s is partially intercepted. Use --force if you want to continue.' % (tool_name,))
            abort()

    if is_all_intercepted(tool_name):
        print('%s is completely intercepted.' % (tool_name,))
        abort()

    for path in filter_whereis(tool_name):
        if not is_intercepted(path):
            intercept_path(tool_name, path)

    try:
        load_config_for(tool_name, None)
        print('Config for %s already exists' % (tool_name,))
    except KeyError:
        print('Config for %s not found, creating a fresh one' % (tool_name,))
        Configuration(app_name=tool_name).save()
    except ValueError:
        print('Config for %s exists, but is invalid. Usage of %s will be impossible until '
              'this is fixed' % (tool_name, tool_name))


def unintercept_tool(tool_name: str):
    if not can_be_unintercepted(tool_name):
        if not FORCE:
            print('%s cannot be unintercepted. Use --force to proceed' % (tool_name,))
            abort()

    for path in filter_whereis(tool_name):
        if is_intercepted(path):
            unintercept_path(path)
        else:
            print('Skipping on %s' % (path,))
    print('Unintercepted %s, leaving the configuration in-place' % (tool_name,))


def check(tool_name: str):
    total_interception = is_all_intercepted(tool_name)
    partial_interception = is_partially_intercepted(tool_name, True)
    if not total_interception and not partial_interception:
        print('%s is not intercepted at all' % (tool_name,))
        sys.exit(0)

    if partial_interception:
        print('''%s is partially intercepted. To clean this up, call:
intercept %s --force
''' % (tool_name, tool_name))

    cfg_exists = False
    try:
        cfg = load_config_for(tool_name, None)
        cfg_exists = True
        print('Configuration for %s exists and is valid' % (tool_name,))
    except ValueError as e:
        print('Configuration for %s is invalid JSON.\nDetails: %s' % (tool_name, e.args[0]))
    except KeyError:
        print('%s configuration not found, creating a new one' % (tool_name,))
        cfg = Configuration(app_name=tool_name)
        cfg_exists = True
    if cfg_exists:
        if os.path.islink(cfg.path):
            target = os.readlink(cfg.path).split('/')[-1]
            print('%s config is a symlink to %s config' % (tool_name, target))
        cfg.save()


def link(app_name, target_name, copy=False):
    assert_intercepted(app_name)
    assert_intercepted(target_name)
    source = os.path.join('/etc/interceptor.d', app_name)
    target = os.path.join('/etc/interceptor.d', target_name)
    if os.path.islink(source) and not FORCE and not copy:
        print('Refusing to link, since %s is already a symlink!' % (app_name,))
        abort()
    with silence_excs(IOError):
        os.unlink(target)
    if copy:
        shutil.copy(source, target)
    else:
        os.symlink(source, target)
    if not copy:
        print('Linked %s to read from %s\'s config' % (target_name, app_name))
    else:
        print('Copied %s to read from %s\'s config' % (target_name, app_name))


def assert_etc_interceptor_d_exists():
    if not os.path.exists('/etc/interceptor.d'):
        print('/etc/interceptor.d does not exist, creating...')
        os.mkdir('/etc/interceptor.d')


def edit(app_name):
    assert_intercepted(app_name)
    editor = list(filter_whereis('nano', abort_on_failure=False))
    if not editor:
        editor = list(filter_whereis('vi', abort_on_failure=False))
        if not editor:
            print('Neither nano nor vi were found')
            abort()
    os.execv(editor[0], [editor[0], os.path.join('/etc/interceptor.d', app_name)])


def reset(app_name):
    assert_intercepted(app_name)
    path = os.path.join('/etc/interceptor.d', app_name)
    if os.path.islink(path):
        target = os.readlink(path).split('/')[-1]
        print('%s config was previously a symlink to %s' % (app_name, target))
    os.unlink(path)
    Configuration(app_name=app_name).save()
    print('Configuration for %s reset' % (app_name, ))


def configure(op_name, app_name, target_name):
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
