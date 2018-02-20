import glob
import os.path

conffiles = glob.glob(os.path.join(os.path.dirname(__file__), 'settings_inc/common', '*.py'))
conffiles.sort()
for f in conffiles:
    exec(open(os.path.abspath(f)).read())

conffiles = glob.glob(os.path.join(os.path.dirname(__file__), 'settings_inc/development', '*.py'))
conffiles.sort()
for f in conffiles:
    exec(open(os.path.abspath(f)).read())