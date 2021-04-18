#!/usr/bin/python3
from satella.files import split

from interceptor.config import load_config_for
import os
import sys

if __name__ == '__main__':
    *_, tool_name = split(sys.argv[0])
    cfg = load_config_for(tool_name)
    args = cfg.modify(sys.argv)

    os.execv(tool_name+'-intercepted', args)
