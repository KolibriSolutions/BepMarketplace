from django import template

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
