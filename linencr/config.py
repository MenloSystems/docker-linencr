# -*- coding: UTF-8 -*-

import os
import sys
import yaml

candidates = [
    'localdata/config.yml',
    '/run/secrets/config.yml'
]
for f in candidates:
    if os.path.isfile(f):
        conf_file = f
        break

if 'conf_file' not in globals():
    print("No configuration file found.")
    print("Fatal.")
    sys.exit()

try:
    with open(conf_file) as f:
        Config = yaml.load(f, Loader=yaml.FullLoader)
except yaml.YAMLError as exc:
    print(("Error in configuration file:", exc))
    print("Fatal.")
    sys.exit()
