import difflib
import re

from .utils import get_all_projects

# regex pattern matching checks:
content_policies = (
    (re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,6}\b'),
     'Email address in text'),
    # disabled ascii checks, because all text fields are filtered in clean_text
    # (re.compile(
    #     r'([\x00-\x08])|([\x0b-\x0c])|([\x0e-\x1f])|([\uFFF0-\uFFFF])|([\u2000-\u200F])|([\u2028-\u202F])|([\x80-\x9F])|([\uE000-\uF8FF])'),
    #  'ASCII control characters in text'),
    # (re.compile(r'\xa0'),
    #  'Non breaking space characters in text'),
)
# minimum text length requirements in chars
length_requirements = {'Title': 10, 'GeneralDescription': 100, 'StudentsTaskDescription': 100}


def cpv_regex(old=False):
    """
    Content policy violations regex check. Checks for 'forbidden' patterns in projects as defined in 'content_policies'

    :param old: Whether to also taak old projects into account.
    :return:
    """
    results = []
    locations = ['Title', 'GeneralDescription', 'StudentsTaskDescription']
    for proj in get_all_projects(old=old):  # test for all timeslots
        for policy in content_policies:
            for location in locations:
                result = policy[0].search(getattr(proj, location).replace('\r', ' ').replace('\n', ' '))
                if result is not None:
                    results.append(
                        {'id': proj.id, 'policy': policy[1], 'matchstring': result.group(), 'start': result.start(),
                         'location': location})
    return results


def cpv_length(old=False):
    """
    Minimum length requirement for some fields.

    :param old:
    :return:
    """
    results = []
    for proj in get_all_projects(old=old):
        for key, value in length_requirements.items():
            text = getattr(proj, key)
            length = len(text)
            if length < value:
                results.append(
                    {'id': proj.id, 'location': key, 'text': text, 'length': length})
    return results


def cpv_diff(old=False):
    """
    Content policy violations diff check
    Test differences between projects in the current timeslot.

    :param old: Whether to look at old proposals as well.
    :return:
    """
    # diff checks
    locations = ['Title', 'GeneralDescription', 'StudentsTaskDescription']
    results = []
    all_projs = list(get_all_projects(old=old))  # only from current timeslot
    projs_done = []
    for proj1 in all_projs:
        for location in locations:
            for proj2 in all_projs:
                if proj1 == proj2:
                    continue
                if proj2 in projs_done:
                    continue
                t1 = getattr(proj1, location).replace('\r', ' ').replace('\n', ' ')
                t2 = getattr(proj2, location).replace('\r', ' ').replace('\n', ' ')
                ratio = difflib.SequenceMatcher(None, t1, t2).real_quick_ratio()
                if ratio > 0.9:
                    ratio = difflib.SequenceMatcher(None, t1, t2).ratio()
                    if ratio > 0.9:
                        results.append(
                            {'id1': proj1.id, 'id2': proj2.id, 'str1': t1, 'str2': t2,
                             'ratio': round(ratio, 3), 'location': location})
        projs_done.append(proj1)
    return results
