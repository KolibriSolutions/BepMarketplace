"""
Automatic distribution of proposals
"""
from random import shuffle

from django.conf import settings
from django.core.exceptions import MultipleObjectsReturned, ValidationError
from django.db.models import Q

from general_model import print_list
from general_view import get_all_students
from general_view import get_timeslot
from index.models import Track
from proposals.utils import get_all_proposals
from students.models import Application


class DistributionProposal:
    """
    A class used as struct to store a suggested distribution of a student to a proposal
    """
    StudentID = -1
    ProjectID = -1
    # -1 = random choice
    # 0 = private project
    # 1-5 = application priority
    Preference = -1

    def __init__(self, StudentID, ProjectID, Preference):
        self.StudentID = StudentID
        self.ProjectID = ProjectID
        self.Preference = Preference

    def as_json(self):
        """

        :return:
        """
        return {
            'StudentID': self.StudentID,
            'ProjectID': self.ProjectID,
            'Preference': self.Preference,
        }

    def __str__(self):
        return "student {} to proposal {} with preference {}".format(self.StudentID, self.ProjectID, self.Preference)


def get_cohorts():
    """
    Get all cohorts that have students in this year.

    :return:
    """
    cohorts = []
    for s in get_all_students().select_related('usermeta'):
        c = s.usermeta.Cohort
        if c is not None:
            if c not in cohorts:
                cohorts.append(c)
    cohorts.sort(reverse=True)

    return cohorts


def get_valid_proposals():
    """
    Get all proposals that (non-private) students can be distributed to.

    :return:
    """
    return get_all_proposals().filter(Q(Status=4) & Q(Private__isnull=True))


def get_valid_students():
    """
    All students with applications, without personal, in this timeslot.

    :return: list of user objects.
    """
    return get_all_students().filter(personal_proposal__isnull=True, applications__isnull=False).filter(applications__Proposal__TimeSlot=get_timeslot()).distinct()
    # usermeta__ECTS__gt=0).distinct()


def distribute_personal(distribution_proposals, students_done=[]):
    """
    Distribute all students with a private proposal to the private proposal.

    :param distribution_proposals: List of distributions
    :param students_done: list of distributed students
    :return:
    """
    stds = get_all_students().filter(personal_proposal__isnull=False, personal_proposal__TimeSlot=get_timeslot()).distinct().prefetch_related('personal_proposal')
    for s in stds:
        try:
            p = s.personal_proposal.filter(TimeSlot=get_timeslot()).get()
        except MultipleObjectsReturned:
            raise Exception("User {} has multiple private proposals ({}). Please resolve this!"
                            .format(s, print_list(s.personal_proposal.filter(TimeSlot=get_timeslot()).all())))
        if p.TimeSlot != get_timeslot():
            raise Exception("User {} of this timeslot has private proposal {} of other timeslot {}"
                            .format(s, p, p.TimeSlot))
        distribution_proposals.append(DistributionProposal(s.id, p.id, 0))
        students_done.append(s)
    return [distribution_proposals, students_done]


def distribute_remaining_random(distribution_proposals, students_done=[]):
    """
    Distribute all remaining students random.

    :param distribution_proposals, students_done: List of distributions and list of distributed students
    :return:
    """
    stds = get_valid_students()
    # attach students to proposals with not enough students
    # attach students to proposals random
    proposals = get_valid_proposals().order_by('?')
    not_distributed = set(stds) - set(students_done)
    for s in not_distributed:  # each not distributed user, distribute random.
        for p in proposals:  # find first proposal with too few students, to add this student to.
            missing_students = p.NumStudentsMin - count_distributions(p.id, distribution_proposals)
            if missing_students > 0:
                # proposal doesn't have enough students
                # distribute student
                distribution_proposals.append(DistributionProposal(s.id, p.id, -1))
                students_done.append(s)
                missing_students -= 1
                break

    # attach students to proposals not yet at maximum.
    # attach students to proposals random
    not_distributed = set(stds) - set(students_done)
    for s in not_distributed:  # each not distributed user, distribute random.
        for p in proposals:  # find first proposal not at max students, to add this student to.
            missing_students = p.NumStudentsMax - count_distributions(p.id, distribution_proposals)
            if missing_students > 0:
                # proposal can handle more students
                # distribute student
                distribution_proposals.append(DistributionProposal(s.id, p.id, -1))
                students_done.append(s)
                missing_students -= 1
                break
    return [distribution_proposals, students_done]


def count_distributions(proposalId, distributionList):
    """
    count number of students distributed to a proposal

    :param proposalId:
    :param distributionList:
    :return:
    """
    count = 0
    for d in distributionList:
        if d.ProjectID == proposalId:
            count += 1

    return count


def calculate_1_from_student(distribute_random, automotive_preference):
    """
    option1, calculated old way. Look for proposals for each student.

    :return:
    """
    # valid students:
    stds = get_valid_students()

    # list of students processed but not in distributionproposal
    students_done = []  # list of student objects
    projects_done = []
    distribution_proposals = []  # list of DistributionProposal objects

    # personal proposals:
    distribution_proposals, students_done = distribute_personal(distribution_proposals, students_done)

    # get all cohorts
    cohorts = get_cohorts()

    # loop over all cohorts, take the youngest students first
    if automotive_preference:
        # for AU students in AU applications
        track_automotive = Track.objects.get(Name='Automotive')
        for c in cohorts:
            # get students in this cohort with applications, ordered by ECTS
            stds_c = list(
                stds.filter(Q(usermeta__Cohort=c) & Q(usermeta__Study__contains='Automotive')).distinct().order_by(
                    '-usermeta__ECTS'))
            # filter on students without distributionproposal
            # Higher application have priority over ECTS
            for n in range(1, settings.MAX_NUM_APPLICATIONS + 1):
                # all students in this cohort, ordered by most ECTS first, with application number a
                stds_c = list(set(stds_c) - set(students_done))
                for s in stds_c:
                    # loop over applications. Lower choices have priority over ects/cohort
                    if s not in students_done:
                        try:
                            application = s.applications.filter(Proposal__TimeSlot=get_timeslot()).get(Priority=n)
                        except Application.DoesNotExist:
                            # user does not have a'th application
                            continue
                        if application.Proposal.Track != track_automotive:
                            break
                        # apply to proposal:
                        proposal = application.Proposal
                        if proposal.TimeSlot != get_timeslot():
                            # application is to an invalid proposal
                            continue
                        num_dist = count_distributions(proposal.id, distribution_proposals)
                        max_dist = proposal.NumStudentsMax
                        if num_dist < max_dist:
                            # proposal can handle more students
                            distribution_proposals.append(DistributionProposal(s.id, proposal.id, n))
                            # remove this student from queryset because it is now distributed
                            students_done.append(s)
                        #else: this might be a tie between students, check and if yes log.

    # loop over all cohorts, take the youngest students first
    # for all students
    for c in cohorts:
        # get students in this cohort with applications, ordered by ECTS
        stds_c = list(stds.filter(Q(usermeta__Cohort=c)).distinct().order_by('-usermeta__ECTS'))
        # filter on students without distributionproposal
        # Higher application have priority over ECTS
        for n in range(1, settings.MAX_NUM_APPLICATIONS + 1):
            # all students in this cohort, ordered by most ECTS first, with application number a
            stds_c = list(set(stds_c) - set(students_done))
            for s in stds_c:
                # loop over applications. Lower choices have priority over ects/cohort
                if s not in students_done:
                    try:
                        application = s.applications.filter(Proposal__TimeSlot=get_timeslot()).get(Priority=n)
                    except Application.DoesNotExist:
                        # user does not have a'th application
                        continue

                    # apply to proposal:
                    proposal = application.Proposal
                    if proposal.TimeSlot != get_timeslot():
                        # application is to an invalid proposal
                        continue

                    num_dist = count_distributions(proposal.id, distribution_proposals)
                    max_dist = proposal.NumStudentsMax

                    if num_dist < max_dist:
                        # proposal can handle more students
                        distribution_proposals.append(DistributionProposal(s.id, proposal.id, n))
                        # remove this student from queryset because it is now distributed
                        students_done.append(s)
                    #else: this might be a tie between students, check and if yes log.

    if distribute_random:
        distribution_proposals, students_done = distribute_remaining_random(distribution_proposals, students_done)

    # return the list of distributed students
    return distribution_proposals


def calculate_2_from_project(distribute_random, automotive_preference):
    """
    Type 2, calculated new way. Loop over proposals and find a student for it.

    :return:
    """
    projects = list(get_valid_proposals().select_related())
    shuffle(projects)
    students_done = []  # list of student objects
    projects_done = []  # list of proposal objects
    distribution_proposals = []  # list of DistributionProposal objects

    distribution_proposals, students_done = distribute_personal(distribution_proposals, students_done)

    # iterate for all preferences twice
    # once to first handle all automotive
    # second time the leftovers plus ele
    if automotive_preference:
        track_automotive = Track.objects.get(Name='Automotive')
        for n in range(1, settings.MAX_NUM_APPLICATIONS + 1):
            # iterate all projects
            for proj in projects:
                # skip non AU
                if proj.Track != track_automotive:
                    continue
                # select all applicants of current selected cohort and preference, sort it for cohort >  ects > random
                apps = list(proj.applications.filter(Priority=n, Proposal__TimeSlot=get_timeslot()).distinct().select_related() \
                            .order_by('-Student__usermeta__Cohort', '-Student__usermeta__ECTS', '?'))
                assigned = count_distributions(proj.id, distribution_proposals)
                # while project is not yet full
                while assigned != proj.NumStudentsMax:
                    # take first from list and check if not yet distributed
                    # if list of applications is empty move on
                    if len(apps) == 0:
                        break
                    app = apps.pop(0)
                    # check if student is automotive
                    if (not app.Student.usermeta.Study) or ('Automotive' not in app.Student.usermeta.Study):
                        continue  # not automotive.
                    # check if there is not an ele project at higher preference for this student, than wait for next round
                    students_appls = app.Student.applications.filter(Priority__lt=app.Priority, Proposal__TimeSlot=get_timeslot()).distinct()
                    students_appls = [True if a.Proposal.Track != track_automotive else False for a in students_appls]
                    if True in students_appls:
                        continue
                    if app.Student not in students_done:
                        # put it in the distribute list to this proposal
                        distribution_proposals.append(DistributionProposal(app.Student_id, proj.id, n))
                        students_done.append(app.Student)
                        assigned += 1
                if assigned == proj.NumStudentsMax:
                    projects_done.append(proj)

    # all students not only au
    for n in range(1, settings.MAX_NUM_APPLICATIONS + 1):
        # iterate all projects
        for proj in projects:
            # select all applicatants of current selected cohort and preference, sort it for cohort >  ects > random
            apps = list(proj.applications.filter(Priority=n, Proposal__TimeSlot=get_timeslot()).distinct().select_related() \
                        .order_by('-Student__usermeta__Cohort', '-Student__usermeta__ECTS', '?'))
            assigned = count_distributions(proj.id, distribution_proposals)
            # while project is not yet full
            while assigned != proj.NumStudentsMax:
                # take first from list and check if not yet distributed
                # if list of applications is empty move on
                if len(apps) == 0:
                    break
                app = apps.pop(0)
                if app.Student not in students_done:
                    # put it in the distribute list to this proposal
                    distribution_proposals.append(DistributionProposal(app.Student_id, proj.id, n))
                    students_done.append(app.Student)
                    assigned += 1
            if assigned == proj.NumStudentsMax:
                projects_done.append(proj)

    # distribute leftover students random
    if distribute_random:
        distribution_proposals, students_done = distribute_remaining_random(distribution_proposals, students_done)

    return distribution_proposals
