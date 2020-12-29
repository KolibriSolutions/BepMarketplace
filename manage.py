#!/usr/bin/env python

#  Bep Marketplace ELE
#  Copyright (c) 2016-2021 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "BepMarketplace.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
