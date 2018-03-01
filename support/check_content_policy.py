def regexTest(stdout=False):
    """

    :param stdout:
    :return:
    """
    from proposals.models import Proposal
    import re
    results = []
    locations = ['Title', 'GeneralDescription', 'StudentsTaskDescription']
    # regex checks:
    policies = (
                (re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,6}\b'),
                'Email address in text'),
                (re.compile(r'([\x00-\x08])|([\x0b-\x0c])|([\x0e-\x1f])|([\uFFF0-\uFFFF])|([\u2000-\u200F])|([\u2028-\u202F])|([\x80-\x9F])|([\uE000-\uF8FF])'),
                 'ASCII control characters in text'),
                (re.compile(r'\xa0'),
                 'Non breaking space characters in text'),
    )
    for prop in Proposal.objects.all():  # test for all timeslots
        for policy in policies:
            for location in locations:
                result = policy[0].search(getattr(prop,location).replace('\r', ' ').replace('\n', ' '))
                if result is not None:
                    if stdout:
                        print(
                            "proposal {} violated policy '{}' in {} with matchstring: '{}'".format(prop.id,
                                                               policy[1], location, result.group()))
                    else:
                        results.append({'id': prop.id, 'policy': policy[1], 'matchstring': result.group(), 'start':result.start() , 'location':location})
    return results


def diffTest(stdout=False):
    """

    :param stdout:
    :return:
    """
    import difflib
    from proposals.utils import get_all_proposals
    # diff checks
    locations = ['Title', 'GeneralDescription', 'StudentsTaskDescription']
    results = []
    allprops = list(get_all_proposals())  # only from current timeslot
    props_todo = list(allprops)
    for prop1 in allprops:
        for location in locations:
            for prop2 in props_todo:
                if prop1 == prop2:
                    continue
                t1 = getattr(prop1, location).replace('\r', ' ').replace('\n', ' ')
                t2 = getattr(prop2, location).replace('\r', ' ').replace('\n', ' ')
                ratio = difflib.SequenceMatcher(None, t1, t2).real_quick_ratio()
                if ratio > 0.9:
                    ratio = difflib.SequenceMatcher(None, t1, t2).ratio()
                    if ratio > 0.9:
                        results.append(
                        {'id1': prop1.id, 'id2': prop2.id, 'str1': t1, 'str2': t2,
                         'ratio': round(ratio,3), 'location': location})
        props_todo.remove(prop1)
    return results


if __name__ == '__main__':
    import django
    import argparse
    import sys
    import os

    parser = argparse.ArgumentParser(description="prints project ids that violate content policy")
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

    regexTest(stdout=True)
