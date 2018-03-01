"""
Automatic distribution of proposals
"""
from random import shuffle

from django.conf import settings
from django.db.models import Q

from general_view import get_all_students
from proposals.utils import get_all_proposals
from index.models import Track


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
            'StudentID' : self.StudentID,
            'ProjectID' : self.ProjectID,
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
    for s in get_all_students():
        c = s.usermeta.Cohort
        if c is not None:
            if c not in cohorts:
                cohorts.append(c)
    cohorts.sort(reverse=True)

    return cohorts

def getValidProposals():
    """
    Get all proposals that (non-private) students can be distributed to.

    :return:
    """
    return get_all_proposals().filter(Q(Status=4) & Q(Private__isnull=True))


def distributePersonal(distributionList):
    """
    Distribute all students with a private proposal to the private proposal.

    :param distributionList: List of distributions
    :return:
    """
    stds = get_all_students().filter(personal_proposal__isnull=False)
    for s in stds:
        # will crash if user has multiple private proposals
        pid = s.personal_proposal.get().id
        distributionList.append(DistributionProposal(s.id, pid, 0))

    return distributionList


def CalculateFromProjects():
    """
    Option 2, calculated new way. Loop over proposals and find a student for it.

    :return:
    """
    projects = list(getValidProposals())
    shuffle(projects)
    studentsdone = []
    projectsdone = []
    distobjs = []

    # iterate for all preferences twice
    # once to first handle all automotive
    # second time the leftovers plus ele
    autrack = Track.objects.get(Name='Automotive')

    for n in range(1, settings.MAX_NUM_APPLICATIONS + 1):
        # iterate all projects
        for proj in projects:
            # skip non AU
            if proj.Track != autrack:
                continue
            # select all applicatants of current selected cohort and preference, sort it for cohort >  ects > random
            apps = list(proj.applications.filter(Priority=n).distinct()\
                        .order_by( '-Student__usermeta__Cohort', '-Student__usermeta__ECTS', '?'))
            assigned = count_applications(proj.id, distobjs)
            # while project is not yet full
            while assigned != proj.NumstudentsMax:
                # take first from list and check if not yet distributed
                # if list of applications is empty move on
                if len(apps) == 0:
                    break
                app = apps.pop(0)
                # check if student is automotive
                if 'Automotive' not in app.Student.usermeta.Study:
                    continue
                # check if there is not an ele project at higher preference for this student, than wait for next round
                appsstudent = app.Student.applications.filter(Priority__lt=app.Priority)
                appsstudent = [True if a.Proposal.Track != autrack else False for a in appsstudent]
                if True in appsstudent:
                    continue
                if app.Student_id not in studentsdone:
                    # put it in the distribute list to this proposal
                    distobjs.append(DistributionProposal(app.Student_id, proj.id, n))
                    studentsdone.append(app.Student_id)
                    assigned += 1
            if assigned == proj.NumstudentsMax:
                projectsdone.append(proj.id)

    # all students not only au
    for n in range(1, settings.MAX_NUM_APPLICATIONS + 1):
        # iterate all projects
        for proj in projects:
            # select all applicatants of current selected cohort and preference, sort it for cohort >  ects > random
            apps = list(proj.applications.filter(Priority=n).distinct()\
                        .order_by( '-Student__usermeta__Cohort', '-Student__usermeta__ECTS', '?'))
            assigned = count_applications(proj.id, distobjs)
            # while project is not yet full
            while assigned != proj.NumstudentsMax:
                # take first from list and check if not yet distributed
                # if list of applications is empty move on
                if len(apps) == 0:
                    break
                app = apps.pop(0)
                if app.Student_id not in studentsdone:
                    # put it in the distribute list to this proposal
                    distobjs.append(DistributionProposal(app.Student_id, proj.id, n))
                    studentsdone.append(app.Student_id)
                    assigned += 1
            if assigned == proj.NumstudentsMax:
                projectsdone.append(proj.id)

    # apply all privates
    privprops = get_all_proposals().filter(Private__isnull=False).distinct()
    for prop in privprops:
        for std in prop.Private.all():
            distobjs.append(DistributionProposal(std.id, prop.id, 0))

    # give the resultants random project
    students = list(get_all_students().filter(Q(personal_proposal__isnull=True) & Q(applications__isnull=False)).distinct())
    props = list(getValidProposals().order_by('?'))
    for std in students:
        if std.usermeta.ECTS == 0:
            continue
        if std.id not in studentsdone:
            while True:
                prop = props.pop(0)
                if prop.id not in projectsdone:
                    distobjs.append(DistributionProposal(std.id, prop.id, -1))
                    break

    return distobjs



def CalculateFromStudent():
    """
    option1, calculated old way. Look for proposals for each student.

    :return:
    """
    # valid students:
    stds = get_all_students().filter(personal_proposal__isnull=True, applications__isnull=False, usermeta__ECTS__gt=0).distinct()

    # list of distributed students to return
    dists = []

    # list of students processed but not in distributionproposal
    studentsdone = []
    projectsdone = []

    # personal proposals:
    dists=(distributePersonal(dists))

    autrack = Track.objects.get(Name='Automotive')

    # get all cohorts
    cohorts = get_cohorts()

    # loop over all cohorts, take the youngest students first
    # for AU students in AU applications
    for c in cohorts:
        # get students in this cohort with applications, ordered by ECTS
        stds_c = list(stds.filter(Q(usermeta__Cohort=c) & Q(usermeta__Study__contains='Automotive')).distinct().order_by('-usermeta__ECTS'))
        # filter on students without distributionproposal
        # Higher application have priority over ECTS
        for a in range(1, settings.MAX_NUM_APPLICATIONS + 1):
            # all students in this cohort, ordered by most ECTS first, with application number a
            stds_c = list(set(stds_c) - set(studentsdone))
            for s in stds_c:
                # loop over applications. Lower choices have priority over ects/cohort
                if s not in studentsdone:
                    try:
                        application = s.applications.get(Priority=a)
                    except:
                        # user does not have a'th application
                        pass
                    if application.Proposal.Track != autrack:
                        break
                    # apply to proposal:
                    proposal = application.Proposal
                    numdist = count_applications(proposal.id, dists)
                    maxdist = proposal.NumstudentsMax
                    if numdist < maxdist:
                        # proposal can handle more students
                        dists.append(DistributionProposal(s.id, proposal.id, a))
                        # remove this student from queryset because it is now distributed
                        studentsdone.append(s)


    # loop over all cohorts, take the youngest students first
    # for all students
    for c in cohorts:
        # get students in this cohort with applications, ordered by ECTS
        stds_c = list(stds.filter(Q(usermeta__Cohort=c)).distinct().order_by('-usermeta__ECTS'))

        # filter on students without distributionproposal
        # Higher application have priority over ECTS
        for a in range(1, settings.MAX_NUM_APPLICATIONS + 1):
            # all students in this cohort, ordered by most ECTS first, with application number a
            stds_c = list(set(stds_c) - set(studentsdone))
            for s in stds_c:
                # loop over applications. Lower choices have priority over ects/cohort
                if s not in studentsdone:
                    try:
                        application = s.applications.get(Priority=a)
                    except:
                        # user does not have a'th application
                        pass

                    # apply to proposal:
                    proposal = application.Proposal
                    numdist = count_applications(proposal.id, dists)
                    maxdist = proposal.NumstudentsMax
                    if numdist < maxdist:
                        # proposal can handle more students
                        dists.append(DistributionProposal(s.id, proposal.id, a))
                        # remove this student from queryset because it is now distributed
                        studentsdone.append(s)


        if len(stds_c) > 0:
            # attach students to proposals with not enough students
            proposals = getValidProposals().order_by('?')
            for p in proposals:
                if len(stds_c) > 0:
                    missingstudents = p.NumstudentsMin - count_applications(p.id, dists)
                    # proposal doesn't have enough students
                    for s in stds_c:
                        if s not in studentsdone:
                            # distribute student
                            dists.append(DistributionProposal(s.id, p.id, -1))
                            studentsdone.append(s)
                            missingstudents -= 1
                            if missingstudents == 0:
                                break

        if len(stds_c) > 0:
            # attach students to proposals random
            proposals = getValidProposals().order_by('?')
            for p in proposals:
                if len(stds_c) > 0:
                    missingstudents = p.NumstudentsMin - count_applications(p.id, dists)
                    # proposal doesn't have enough students
                    for s in stds_c:
                        if s not in studentsdone:
                            # distribute student
                            dists.append(DistributionProposal(s.id, p.id, -1))
                            studentsdone.append(s)
                            missingstudents -= 1
                            if missingstudents == 0:
                                break
    # return the list of distributed students
    return dists

def count_applications(proposalId, distributionList):
    """

    :param proposalId:
    :param distributionList:
    :return:
    """
    count = 0
    for d in distributionList:
        if d.ProjectID == proposalId:
            count += 1

    return count


