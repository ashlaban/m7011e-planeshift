#! /usr/bin/env python3

import subprocess

res = subprocess.run(['./gfm-md-to-html.rb', 'README.md'], stdout=subprocess.PIPE)

print(res.stdout)