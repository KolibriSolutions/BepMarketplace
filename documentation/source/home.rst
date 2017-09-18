
=============================
BEP Marketplace Documentation
=============================

Welcome to the BEP Marketplace Documentation.

************
Introduction
************

The BEP Marketplace is build as a project from the faculty of Electrical Engineering at the Eindhoven University
of Technology. It is build by Frank Boerman and Jeroen van Oorschot in 2016-2017.

Overview of the system
======================
The website contains a number of proposals (Projects a student can do). These proposals are submitted by staff members.
Staff members can be responsible (type 1) or assistants (type 2) of a proposal. Usually responsible staff are professors
and assistants are PhD'ers or students from a student team. Students are able to apply to any of these proposals that
they like to do. The projects are semi-automatically distributed among the students that applied and start working on
the project. Students then use the system to hand in deliverables. Finally the planning for the presentations of the
projects can be submitted by staff and viewed by all users.

Timephases
==========
To organize the BEP projects, the system is divided in a few phases. The current
phase can be seen in the sidebar on the left.

1. Generating Project Proposals.
   Proposals are created and added to the
   system following the procedure set out in section below.

2. Project Quality Check
   Track heads go through all proposals and approve
   or disapprove proposals. Please note that they can already start doing this
   earlier, but in this phase no new proposals can be added.

3. Students Choosing Projects
   Students can apply to proposals. Only the
   support staff (type 3) can see these applications.

4. Distribution of Proposals
   Projects are automatically distributed across
   all students. This is checked by support staff and can be manually adjusted.

5. Gather and Process Objections
   Short period to gather objections from
   students to their distributions. These have to be within reason. Support
   staff will handle this and can manually adjust distribution where needed.

6. Execution of projects
   The actual doing of projects for 6 months.

7. Presentation of Results
   The students present their results, hand in
   their papers and are graded. These grades will be entered into the
   marketplace system and presented to support staff. Students cannot see these
   grades.

Users and Login
===============
The system knows normal users and superusers. Superusers have access to the godpowers-section and the django-admin panel.
Superuser can login using the 2-factor login available at /two_factor/login/. Normal users log in via the SAML/ADFS
single-signon system. After a new users logs in, he/she is granted type2staffunverified access for a staff member and
normal student access if it is a student. Support staff (type3staff) can change these unverified accounts to type1staff
or normal type2staff.

Structure of code
=================
The code is all Python, using the Django framework. The project is divided in a number of apps. These apps contain
multiple python files, see the Django documentation for their usage. The Templates app contains all HTML templates for
rendering the frontend. A few functions have been put in separate files for clarity and reusability.


*****************
Table of contents
*****************

.. toctree::
    :caption: Table of Contents
    :name: BepMarketplaceDocumentation
    :maxdepth: 3

    api/home
    BepMarketplace/home
    distributions/home
    djangosaml2_custom/home
    download/home
    godpowers/home
    index/home
    presentations/home
    professionalskills/home
    proposals/home
    results/home
    students/home
    support/home
    templates/home
    timeline/home
    tracking/home
    two_factor_custom/home

    general_excel
    general_form
    general_mail
    general_model
    general_view
    MailTrackHeadsPending
    init_importType1
    init_populate