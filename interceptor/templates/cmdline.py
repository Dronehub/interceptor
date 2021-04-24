#!{EXECUTABLE}
# Generated automatically by interceptor, a tool to intercept calls
# to the commands and to alter their arguments.

# To learn more visit https://github.com/Cervi-Robotics/interceptor
from interceptor.config import load_config_for
import os
import sys

TOOLNAME = '{TOOLNAME}'
LOCATION = '{LOCATION}'
VERSION = '{VERSION}'

if __name__ == '__main__':
    cfg = load_config_for(TOOLNAME, VERSION)
    args = cfg.modify(sys.argv)
    os.execv(LOCATION, args)
