#  Bep Marketplace ELE
#  Copyright (c) 2016-2022 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#
import difflib
import json
import re
import threading
from math import floor

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.conf import settings
from django.core.cache import cache

from .utils import get_all_projects

# regex pattern matching checks:
content_policies = (
    (re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,6}\b'),
     'Email address in text'),
)
# minimum text length requirements in chars
length_requirements = {'Title': 10, 'GeneralDescription': 100, 'StudentsTaskDescription': 100}


def cpv_regex(proj):
    """
    Content policy violations regex check. Checks for 'forbidden' patterns in projects as defined in 'content_policies'

    :param proj: Project to check
    :return:
    """
    results = []
    locations = ['Title', 'GeneralDescription', 'StudentsTaskDescription']
    for policy in content_policies:
        for location in locations:
            result = policy[0].search(getattr(proj, location).replace('\r', ' ').replace('\n', ' '))
            if result is not None:
                results.append({
                    'policy': policy[1],
                    'matchstring': result.group(),
                    'start': result.start(),
                    'location': location
                })
    return results


def cpv_length(proj):
    """
    Minimum length requirement for some fields.

    :param proj: project to check
    :return:
    """
    results = []
    for key, value in length_requirements.items():
        text = getattr(proj, key)
        length = len(text)
        if length < value:
            results.append({
                'location': key,
                'text': text,
                'length': length
            })
    return results


def cpv_diff(proj):
    """
    Content policy violations diff check
    Test differences between projects in the current timeslot.

    :param proj: Project to check
    :return:
    """
    projects_to_check = get_all_projects(old=True).filter(TimeSlot=proj.TimeSlot)
    results = []
    locations = ['Title', 'GeneralDescription', 'StudentsTaskDescription']
    for location in locations:
        t1 = getattr(proj, location).replace('\r', ' ').replace('\n', ' ')
        for proj2 in projects_to_check:  # all projects of the same timeslot
            if proj == proj2:
                continue
            t2 = getattr(proj2, location).replace('\r', ' ').replace('\n', ' ')
            ratio = difflib.SequenceMatcher(None, t1, t2).real_quick_ratio()
            if ratio > 0.9:
                ratio = difflib.SequenceMatcher(None, t1, t2).ratio()
                if ratio > 0.9:
                    results.append({
                        'proj': proj2,
                        # 'str1': t1,  # uncomment this to store the full text of diff in cache.
                        # 'str2': t2,
                        'ratio': round(ratio, 3),
                        'location': location
                    })
    return results


class CPVCheckThread(threading.Thread):
    """
    Same as email thread but with a template.
    input is array of mails with subject, template and destination
    """

    def __init__(self, projects):
        if not hasattr(projects, '__iter__'):
            projects = [projects]
        self.projects = projects
        super().__init__()
        self.channel_layer = get_channel_layer()

    def run(self):
        for i, proj in enumerate(self.projects):
            if not proj:
                continue
            if not settings.TESTING:
                async_to_sync(self.channel_layer.group_send)('cpv_progress',
                                                             {'type': 'update', 'text': json.dumps({
                                                                 'progress': floor(((i + 1) / len(self.projects)) * 100),
                                                             })})
                cpv_length_result = cpv_length(proj)
                cpv_diff_result = cpv_diff(proj)
                cpv_regex_result = cpv_regex(proj)
                if cpv_length_result or cpv_diff_result or cpv_regex_result:
                    cache.set('cpv_proj_{}'.format(proj.pk), {
                        'project': proj,
                        'pattern_violations': cpv_regex_result,
                        'length_violations': cpv_length_result,
                        'diff_violations': cpv_diff_result,
                    }, None)
