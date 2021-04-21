import copy
import json
import os
import typing as tp

from satella.coding import for_argument
from satella.files import write_to_file
from satella.json import read_json_from_file, write_json_to_file


class Configuration:
    def __init__(self, args_to_take_away: tp.Optional[tp.List[str]] = None,
                 args_to_append: tp.Optional[tp.List[str]] = None,
                 args_to_append_before: tp.Optional[tp.List[str]] = None,
                 args_to_replace: tp.Optional[tp.List[tp.Tuple[str, str]]] = None,
                 display_before_start: bool = False):
        self.args_to_take_away = args_to_take_away or []
        self.args_to_append = args_to_append or []
        self.args_to_append_before = args_to_append_before or []
        self.args_to_replace = args_to_replace or []
        self.display_before_start = display_before_start
        self.app_name = None

    def to_json(self):
        return {'args_to_take_away': self.args_to_take_away,
                'args_to_append': self.args_to_append,
                'args_to_append_before': self.args_to_append_before,
                'args_to_replace': self.args_to_replace,
                'display_before_start': self.display_before_start}

    @for_argument(None, copy.copy)
    def modify(self, args, *extra_args):
        process, *arguments = args
        for arg_to_take_away in self.args_to_take_away:
            if arg_to_take_away in arguments:
                del arguments[arguments.index(arg_to_take_away)]

        for arg_to_append in self.args_to_append:
            if arg_to_append not in arguments:
                arguments.append(arg_to_append)

        for arg_to_append_before in self.args_to_append_before:
            if arg_to_append_before not in arguments:
                arguments = [arg_to_append_before] + arguments

        for arg_to_replace, arg_to_replace_with in self.args_to_replace:
            if arg_to_replace in arguments:
                arguments[arguments.index(arg_to_replace)] = arg_to_replace_with

        if self.display_before_start:
            print('%s %s' % (self.app_name, ' '.join(arguments)))

        return [process, *arguments]

    def save(self):
        write_json_to_file(os.path.join('/etc/interceptor.d', self.app_name), self.to_json(),
                           sort_keys=True,
                           indent=4)

    @classmethod
    def from_json(cls, dct):
        return Configuration(dct.get('args_to_take_away'),
                             dct.get('args_to_append'),
                             dct.get('args_to_append_before'),
                             dct.get('args_to_replace'),
                             dct.get('display_before_start', False))


def load_config_for(name: str) -> Configuration:
    file_name = os.path.join('/etc/interceptor.d', name)
    if not os.path.exists(file_name):
        raise KeyError('Configuration for %s does not exist' % (name, ))

    cfg = Configuration.from_json(read_json_from_file(file_name))
    cfg.app_name = name
    return cfg
