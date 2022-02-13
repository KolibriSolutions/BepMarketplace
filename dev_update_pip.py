#  Bep Marketplace ELE
#  Copyright (c) 2016-2022 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#
"""
script to update all pip packages.
"""

import pip
from subprocess import call

# code snippet to update all pip packages.
if __name__ == "__main__":
    for dist in pip.get_installed_distributions():
        print("installing: " + dist.project_name)
        call("pip install --upgrade " + dist.project_name, shell=True)
