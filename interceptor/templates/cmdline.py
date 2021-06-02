#!{EXECUTABLE}

# Generated automatically by interceptor, a tool to intercept calls
# to the commands and to alter their arguments.

# To learn more visit https://github.com/Dronehub/interceptor

import os
import sys
from interceptor.config import load_config_for

TOOLNAME = '{TOOLNAME}'
LOCATION = '{LOCATION}'
VERSION = '{VERSION}'

if __name__ == '__main__':
    cfg = load_config_for(TOOLNAME, VERSION)
    args = cfg.modify(sys.argv)
    os.execv(LOCATION, args)
