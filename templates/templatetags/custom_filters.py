#  Bep Marketplace ELE
#  Copyright (c) 2016-2020 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#
from django import template

from general_model import print_list

register = template.Library()


@register.filter(name="index")
def index(lst, i):
    """
    Return a value from a list at index

    :param lst: list
    :param i: index
    :return:
    """
    return lst[int(i)]


@register.filter(name='to_list')
def to_list(obj):
    """
    Convert object to list

    :param obj:
    :return: list of object
    """
    return list(obj)


@register.simple_tag
def get_hash():
    """
    Get the git has from the system to show the current revision.

    :return:
    """
    try:
        with open("githash", "r") as stream:
            h = stream.readlines()[0].strip('\n')
        return h[:10]
    except FileNotFoundError:
        return "None"


@register.filter(name='print_list')
def print_list_tag(list):
    return print_list(list)
