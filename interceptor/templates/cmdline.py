#!{EXECUTABLE}
from interceptor.config import load_config_for
import os
import sys

if __name__ == '__main__':
    tool_name = sys.argv[0].split('/')[-1]
    cfg = load_config_for(tool_name)
    args = cfg.modify(sys.argv)
    os.execv(args[0], args)
