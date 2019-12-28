#  Bep Marketplace ELE
#  Copyright (c) 2016-2019 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE

import re
# from hashlib import sha256

import bleach
# from asgiref.sync import async_to_sync
# from channels.layers import get_channel_layer
from django.conf import settings
# from django.core.cache import cache
# from django.core.exceptions import ValidationError
# from django.core.validators import URLValidator
from markdown import markdown

# from virustotal.models import CheckedUrl

# link_regex = re.compile(settings.LINKREGEX)


def markdown_safe(payload):
    """
    Filter HTML output of markdown based on whitelist of allowed HTML tags.

    :param payload:
    :return:
    """
    md = shift_markdown_headings(payload)  # shift headers to remove h1 and h2
    md = markdown(
        text=md,
        extensions=['nl2br'],  # newline to linebreak
    )  # generate markdown
    return bleach.clean(md, tags=bleach.ALLOWED_TAGS + [  # clean generated html
        'img',
        'p',
        'br',
        # 'h1',
        # 'h2',
        'h3',
        'h4',
        'h5',
        'h6',
    ], attributes={
        'a': ['href', 'title'],
        'img': ['src', 'title', 'width', 'height'],
    })


def shift_markdown_headings(md):
    """
    Shift headers in markdown one level down, to not interfere with other headings.

    :param md:
    :return:
    """
    for i in reversed(list(range(1, 7))):
        md = re.sub(r'^#{' + str(i) + r'}(?!\s|#)', '#' * (i + 2) + ' ', md, flags=re.MULTILINE)  # for headers without space after hash
        md = re.sub(r'^#{' + str(i) + r'}(?=\s)', '#' * (i + 2), md, flags=re.MULTILINE)  # for headers with space after hash
    return md

#
# def markdown_link_checker(markdown):
#     email_reg = re.compile(settings.EMAILREGEXCHECK)
#     val = URLValidator()
#     channel_layer = get_channel_layer()
#
#     for result in list(link_regex.finditer(markdown)):
#         link = result.group(2)
#         try:
#             val(link)
#         except ValidationError:
#             markdown = markdown.replace(result.group(), '[{}][<i>Invalid Link</i>]'.format(result.group(1)))
#             continue
#         if 'mailto' == result.group(2).split(':')[0]:
#             try:
#                 if email_reg.fullmatch(result.group(2).split(':')[1]) is not None:
#                     markdown = markdown.replace(result.group(),
#                                                 '<a href="{}">{}</a>'.format(result.group(2).split('?')[0],
#                                                                              result.group(1)))
#                 else:
#                     markdown = markdown.replace(result.group(),
#                                                 '[{}][<i>Invalid Email in mailto]</i>'.format(result.group(1)))
#             except:
#                 markdown = markdown.replace(result.group(), '[{}][<i>Invalid Email in mailto</i>]'.format(result.group(1)))
#             continue
#
#         h = sha256(link.encode()).hexdigest()
#         report = cache.get('virustotal:' + h)
#         if isinstance(report, str):
#             markdown = markdown.replace(result.group(),
#                                         '[{}][<i>Link is being checked by the system, please come back later</i>]'.format(
#                                             result.group(1)))
#             continue
#         if report is None:
#             try:
#                 report = CheckedUrl.objects.get(URL=link)
#                 cache.set('virustotal:' + h, report, 24 * 60 * 60)
#             except CheckedUrl.DoesNotExist:
#                 async_to_sync(channel_layer.send)(
#                     'virustotal', {
#                         'type': 'checklink',
#                         'link': result.group(2)
#                     }
#                 )
#
#                 # link still needs to be checked, block it
#                 markdown = markdown.replace(result.group(), '[{}][<i>Link is being checked by the system, please come back later</i>]'.format(result.group(1)))
#                 continue
#
#         if report.Status == 1:
#             # link is OK so include it
#             markdown = markdown.replace(result.group(), '<a href="{}">{}</a>'.format(result.group(2).split('?')[0],
#                                                                                      result.group(1)))
#         elif report.Status == 2:
#             # link is broken, block it
#             markdown = markdown.replace(result.group(),
#                                         '[{}][<i>This link is disabled because the automatic link checking reported this'
#                                         ' as a broken link. Please contact the project responsible to change the link</i>]'
#                                         .format(result.group(1)))
#         elif report.Status == 3:
#             # link is malware, block it
#             markdown = markdown.replace(result.group(),
#                                         '[{}][<i>This link is disabled because the automatic link checking reported this'
#                                         ' as an unsafe link. Please contact the project responsible to change the link</i>]'
#                                         .format(result.group(1)))
#     return markdown
