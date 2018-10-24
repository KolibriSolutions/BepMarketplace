"""
Mail all trackheads with the proposal that they have to check. (All pending proposals)
This script can be used to automatically mail track heads in (for instance) a cron job.
"""
from general_mail import mail_track_heads_pending

if __name__ == '__main__':
    import django
    import argparse
    import sys
    import os

    parser = argparse.ArgumentParser(description="Load type1 from csv")
    parser.add_argument('--mode', nargs='?', const=1, type=str, default='debug', help='debug/production')

    parser.set_defaults(createDummyData=False)
    MODE = parser.parse_args().mode

    if MODE not in ["debug", "production"]:
        sys.exit(1)
    if MODE == 'debug':
        os.environ['DJANGO_SETTINGS_MODULE'] = 'BepMarketplace.settings_development'
    elif MODE == 'production':
        os.environ['DJANGO_SETTINGS_MODULE'] = 'BepMarketplace.settings'

    django.setup()

    mail_track_heads_pending(stdout=True)
