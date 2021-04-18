#!{EXECUTABLE}
from interceptor.config import load_config_for
import os
import sys

if __name__ == '__main__':
    cfg = load_config_for('{TOOLNAME}')
    args = cfg.modify(sys.argv)
    os.execv('{LOCATION}', args)
