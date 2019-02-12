"""
Initialy populate an empty django database with the required groups, and possibly dummy data for testing.

"""
import argparse
import os
import sys

import django

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Populate the database with initial values")
    parser.add_argument('--mode', nargs='?', const=1, type=str, default='debug', help='debug/production')
    parser.add_argument('--create-dummy-data', dest='createDummyData', action='store_true',
                        help='if activated dummy data is generated')
    parser.set_defaults(createDummyData=False)
    DUMMY, MODE = parser.parse_args().createDummyData, parser.parse_args().mode

    if MODE not in ["debug", "production"]:
        print("Please use --mode debug or --mode production")
        sys.exit(1)

    if MODE == 'debug':
        os.environ['DJANGO_SETTINGS_MODULE'] = 'BepMarketplace.settings_development'
    elif MODE == 'production':
        os.environ['DJANGO_SETTINGS_MODULE'] = 'BepMarketplace.settings'

    django.setup()

    from django.contrib.auth.models import Group, User
    from index.models import Track, Broadcast, UserMeta
    from proposals.models import Proposal
    from students.models import Application, Distribution
    from support.models import CapacityGroupAdministration, CapacityGroup
    from timeline.models import TimePhase, TimeSlot
    import random
    from timeline.utils import get_timeslot

    all_models = [Track, Broadcast, Proposal, Application, Distribution, TimePhase, TimeSlot]

    tracks = [
        ("Automotive", "AU"),
        ("Smart&Sustainable Society", "SSS"),
        ("Connected World", "CW"),
        ("Care&Cure", "C&C"),
    ]

    Groups = (
        ("EES", "Electrical Energy Systems"),
        ("ECO", "Electro-Optical Communications"),
        ("EPE", "Electromechanics and Power Electronics"),
        ("ES", "Electronic Systems"),
        ("IC", "Integrated Circuits"),
        ("CS", "Control Systems"),
        ("SPS", "Signal Processing Systems"),
        ("PHI", "Photonic Integration"),
        ("EM", "Electromagnetics")
    )
    for group in Groups:
        c, created = CapacityGroup.objects.get_or_create(ShortName=group[0], FullName=group[1])
        if created:
            print("creating {}-{}".format(group[0], group[1]))


    print("populating tables with production values")

    # default results
    [{"model": "results.gradecategory", "pk": 1, "fields": {"Weight": 20.0, "Name": "Specialisation", "TimeSlot": 1}},
     {"model": "results.gradecategory", "pk": 2,
      "fields": {"Weight": 20.0, "Name": "Research and design skills", "TimeSlot": 1}},
     {"model": "results.gradecategory", "pk": 3, "fields": {"Weight": 20.0, "Name": "Execution", "TimeSlot": 1}},
     {"model": "results.gradecategory", "pk": 4, "fields": {"Weight": 20.0, "Name": "Report", "TimeSlot": 1}},
     {"model": "results.gradecategory", "pk": 5,
      "fields": {"Weight": 20.0, "Name": "Presentation and defense", "TimeSlot": 1}}]

    # default aspects
    [{"model": "results.gradecategoryaspect", "pk": 1, "fields": {"Category": 1, "Name": "Quality of literature review",
                                                                  "Description": "Orientation on literature, identification of relevant sources, evaluation and interpretation of relevance of sources for the investigation"}},
     {"model": "results.gradecategoryaspect", "pk": 2,
      "fields": {"Category": 1, "Name": "Level of specialised knowledge",
                 "Description": "Level of knowledge and technical skill set relevant for execution of research project"}},
     {"model": "results.gradecategoryaspect", "pk": 3, "fields": {"Category": 1, "Name": "Disciplinary knowledge",
                                                                  "Description": "Broader knowledge on research area, total skill set, insight in scope and context of research, discipline of electrical engineering"}},
     {"model": "results.gradecategoryaspect", "pk": 4,
      "fields": {"Category": 1, "Name": "Ability to connect problem definition to research field/sub-questions",
                 "Description": "Ability to deconstruct research problem(s) in sub-problems, connect to knowledge, and synthesize solutions"}},
     {"model": "results.gradecategoryaspect", "pk": 5,
      "fields": {"Category": 2, "Name": "Formulation of research questions",
                 "Description": "Quantification and clarity of problem formulation, clarity of research for project aims, formulation of sub-goals"}},
     {"model": "results.gradecategoryaspect", "pk": 6,
      "fields": {"Category": 2, "Name": "Quality and quantity of established results",
                 "Description": "Quality of results in terms of scientific and/or functional value. Quantity of results in view of project time"}},
     {"model": "results.gradecategoryaspect", "pk": 7,
      "fields": {"Category": 2, "Name": "Creativity, originality, innovative value",
                 "Description": "Originality of contributions, creativity of solution(s), innovative value"}},
     {"model": "results.gradecategoryaspect", "pk": 8, "fields": {"Category": 2,
                                                                  "Name": "Critical attitude towards results, methodology, scope and perspective of research",
                                                                  "Description": "Ability to critically assess, analyse and defend the relevance of contributions, scientific way of working."}},
     {"model": "results.gradecategoryaspect", "pk": 9, "fields": {"Category": 3, "Name": "Level of independency",
                                                                  "Description": "Pro-activity and independence in the execution and organization of the project, networking activities for acquiring knowledge"}},
     {"model": "results.gradecategoryaspect", "pk": 10, "fields": {"Category": 3, "Name": "Commitment and dedication",
                                                                   "Description": "Commitment in the project, problem-ownership, dedication, general level of responsibility, responsibility as team member"}},
     {"model": "results.gradecategoryaspect", "pk": 11, "fields": {"Category": 3, "Name": "Time planning",
                                                                   "Description": "Effectivity of time planning, ability to adhere to planning or adjust planning where necessary. General timing"}},
     {"model": "results.gradecategoryaspect", "pk": 12, "fields": {"Category": 3, "Name": "Effectiveness",
                                                                   "Description": "Ability to communicate with specialists and peers, organization of research, preparation and effectiveness of technical meetings"}},
     {"model": "results.gradecategoryaspect", "pk": 13, "fields": {"Category": 4, "Name": "Readability of report",
                                                                   "Description": "Formulation, ease of understanding, perceptibility, correctness of English, good use of figures, graphs and tables"}},
     {"model": "results.gradecategoryaspect", "pk": 14, "fields": {"Category": 4, "Name": "Problem formulation",
                                                                   "Description": "Clarity of main objectives, problem definition, formulation of sub-questions"}},
     {"model": "results.gradecategoryaspect", "pk": 15, "fields": {"Category": 4, "Name": "Quality of content",
                                                                   "Description": "Scientific quality of report, clarity of summary, clarity of exposition, clarity of figures, clarity of reasoning, accuracy of proofs, (suitability for publication)"}},
     {"model": "results.gradecategoryaspect", "pk": 16,
      "fields": {"Category": 4, "Name": "Structure and organisation of report",
                 "Description": "Introduction, literature review, problem formulation, methodology, analysis and results, conclusions"}},
     {"model": "results.gradecategoryaspect", "pk": 17,
      "fields": {"Category": 5, "Name": "Coverage of research outcomes",
                 "Description": "Clarity of problem formulation, clarity on contributions and main conclusions from the research. Choice and relevance of presented material"}},
     {"model": "results.gradecategoryaspect", "pk": 18, "fields": {"Category": 5, "Name": "Presentation skills",
                                                                   "Description": "Didactic quality of presentation, clarity, pace, self-confidence, correctness of formulations, accuracy of timing, fitting for audience, ability to attract attention and interest from audience"}},
     {"model": "results.gradecategoryaspect", "pk": 19,
      "fields": {"Category": 5, "Name": "Quality of supporting material",
                 "Description": "Effectiveness of visual support (slides), quality of demonstration, sound or other equipment"}},
     {"model": "results.gradecategoryaspect", "pk": 20, "fields": {"Category": 5, "Name": "Discussion skills",
                                                                   "Description": "Initiative and initiation of discussion, flow and focus in discussion, confidence in responses"}}]

    # setup tracks
    trackobjs = []
    for track in tracks:
        t, created = Track.objects.get_or_create(Name=track[0])
        if created:
            print("creating track {}".format(track[0]))
            t.ShortName = track[1]
            t.save()
        trackobjs.append(t)

    # setup all groups with permissions
    g, created = Group.objects.get_or_create(name='type1staff')
    if created:
        print("creating type1staff")
        # perms = Permission.objects.filter(content_type=ContentType.objects.get_for_model(Proposal))
        # for p in perms:
        #     g.permissions.add(p)
        # #perms = Permission.objects.filter(content_type=ContentType.objects.get_for_model(CategoryResult))
        # g.permissions.add(perms[0])
        # g.permissions.add(perms[1])
        g.save()

    g, created = Group.objects.get_or_create(name='type2staff')
    if created:
        print("creating type2staff")
        # #perms = Permission.objects.filter(content_type=ContentType.objects.get_for_model(Proposal))
        # g.permissions.add(perms[0])
        # g.permissions.add(perms[1])
        # g.permissions.add(perms[2])
        g.save()

    g, created = Group.objects.get_or_create(name='type2staffunverified')
    if created:
        print("creating type2staffunverified")
        # perms = Permission.objects.filter(content_type=ContentType.objects.get_for_model(Proposal))
        # g.permissions.add(perms[0])
        # g.permissions.add(perms[1])
        # g.permissions.add(perms[2])
        g.save()

    g, created = Group.objects.get_or_create(name='type3staff')
    if created:
        print("creating type3staff")
        # for model in all_models:
        #     perms = Permission.objects.filter(content_type=ContentType.objects.get_for_model(model))
        #     for p in perms:
        #         g.permissions.add(p)
        g.save()

    g, created = Group.objects.get_or_create(name='type4staff')
    if created:
        print("creating type4staff")
        for group in Groups:
            grp = CapacityGroupAdministration()
            grp.Group = group[0]
            grp.save()

    g, created = Group.objects.get_or_create(name='type5staff')
    g.save()
    if created:
        print("creating type5staff")

    g, created = Group.objects.get_or_create(name='type6staff')
    g.save()
    if created:
        print("creating type6staff")

    if not DUMMY:
        # End of non dummy generation
        sys.exit(0)

    # generate test users, proposals and applictions for debug purpose
    print("populating tables with debug objects")

    NUMPROFS = 20
    NUMPHDS = 30
    NUMSTDS = 50
    NUMPROPOSALS = 75

    type1staff = Group.objects.get(name="type1staff")
    type2staff = Group.objects.get(name="type2staff")
    type3staff = Group.objects.get(name="type3staff")

    profs = list(type1staff.user_set.all())
    phds = list(type2staff.user_set.all())

    print("creating {} professors".format(NUMPROFS))
    for i in range(0, NUMPROFS):
        try:
            prof = User.objects.create_user('professor{}'.format(i), 'professor{}@tue.nl'.format(i), 'marketplace')
            prof.first_name = "professor"
            prof.last_name = str(i)
            prof.groups.add(type1staff)
            prof.save()
            profs.append(prof)
        except:
            print(str(i) + " not created")
        prof = User.objects.get(username='professor{}'.format(i))
        try:
            mta = UserMeta()
            mta.Fullname = "Professor-" + str(i)
            mta.Studentnumber = 0
            mta.User = prof
            mta.save()
            print("usermeta prof" + str(i))
        except:
            print(str(i) + " prof usermeta not created")

    print("creating {} phders".format(NUMPHDS))
    for i in range(0, NUMPHDS):
        try:
            phd = User.objects.create_user('phd{}'.format(i), 'phd{}@tue.nl'.format(i), 'marketplace')
            phd.first_name = "phd"
            phd.last_name = str(i)
            phd.groups.add(type2staff)
            phd.save()
            phds.append(phd)
        except:
            print(str(i) + " not created")
        phd = User.objects.get(username='phd{}'.format(i))
        try:
            mta = UserMeta()
            mta.Fullname = "phd-" + str(i)
            mta.Studentnumber = 0
            mta.User = phd
            mta.save()
            print("usermeta phd" + str(i))
        except:
            print(str(i) + " phd usermeta not created")

    stds = []
    print("creating {} students".format(NUMSTDS))
    for i in range(0, NUMSTDS):
        try:
            std = User.objects.create_user('std{}'.format(i), 'std{}@tue.nl'.format(i), 'marketplace')
            std.first_name = "std"
            std.last_name = str(i)
            std.save()
            stds.append(std)
        except:
            print(str(i) + " not created")
        std = User.objects.get(username='std{}'.format(i))
        try:
            mta = UserMeta()
            mta.Fullname = "student-" + str(i)
            mta.Studentnumber = str(i) + str(i) + str(i) + str(i) + str(i)
            mta.User = std
            mta.save()
            print("usermeta" + str(i))
        except:
            print(str(i) + " usermeta not created")

    print("creating the support user")
    try:
        supp = User.objects.create_user('janedoe', 'j.doe.1@tue.nl', 'marketplace')
        supp.first_name = "Jane"
        supp.last_name = "Doe"
        supp.groups.add(type3staff)
        supp.save()
    except:
        print("no type3 created")
    supp = User.objects.get(username='janedoe')
    try:
        mta = UserMeta()
        mta.Fullname = 'Jane Doe'
        mta.User = supp
        mta.save()
    except:
        print('Supp usermeta not created')

    print("creating track Head and assigning him")
    try:
        trackh = User.objects.create_user('johndoe', 'j.doe.2@tue.nl', 'marketplace')
        trackh.first_name = "John"
        trackh.last_name = "Doe"
        trackh.groups.add(type1staff)
        trackh.save()
    except:
        print("no trackhead created")
    supp = User.objects.get(username='johndoe')
    try:
        mta = UserMeta()
        mta.Fullname = 'John Doe'
        mta.User = supp
        mta.save()
    except:
        print('Track usermeta not created')

    for track in tracks:
        try:
            t = Track.objects.get(Name=track[0])
            t.Head = trackh
            t.save()
        except:
            print("no track created")


    def flip(x):
        """

        :param x:
        :return:
        """
        return True if random.random() < x else False


    print("creating proposals")
    for i in range(0, NUMPROPOSALS):
        try:
            p = Proposal()
            p.Title = "project{}".format(i)
            p.ResponsibleStaff = random.choice(profs)
            p.Group = random.choice(Groups)[0]  # TODO Change to capacity group model.
            p.NumStudentsMin = random.randint(1, 2)
            p.NumStudentsMax = random.randint(p.NumStudentsMin, 5)
            p.GeneralDescription = "stuff about project. autogenerated with number {}".format(i)
            p.StudentsTaskDescription = "students have to do stuff woop woop"
            p.Track = random.choice(trackobjs)
            # p.Private = None
            # p.Image = random.choice(["niels.png", "crying.png"])
            # p.Status = random.choice(Proposal.StatusOptions)[0]
            p.Status = 4
            p.TimeSlot = get_timeslot()
            p.save()  # save already to activate the manytomany field of assistants
            numphd = random.choice([1, 2])
            ass1 = random.choice(phds)
            p.Assistants.add(ass1)
            if numphd == 2:
                phds.remove(ass1)
                ass2 = random.choice(phds)
                p.Assistants.add(ass2)
                phds.append(ass1)
            p.save()
            print('{} created'.format(p))
        except:
            print(str(i) + "th proposal not created")
