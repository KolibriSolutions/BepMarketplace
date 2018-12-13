from support.models import CapacityGroupAdministration

def group_administrator_status(project, user):
    """
    Returns the administrator status of user for the group belonging to the project
    status 0: no admin
    status 1: admin for this group

    :param project:
    :param user:
    :return:
    """
    try:
        g = CapacityGroupAdministration.objects.get(Group=project.Group, Members=user)
    except CapacityGroupAdministration.DoesNotExist:
        return 0
    return 1


def get_writable_admingroups(user):
    """
    returns group objects for which this user is writable group admin

    :param user:
    :return:
    """
    return [g.Group for g in CapacityGroupAdministration.objects.filter(Members=user)]