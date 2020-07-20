#  Bep Marketplace ELE
#  Copyright (c) 2016-2020 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#
from datetime import datetime

from django.conf import settings
from openpyxl import Workbook
from openpyxl.writer.excel import save_virtual_workbook

from timeline.utils import get_timeslot


def get_list_distributions_xlsx(proposals):
    """
    Excel export of proposals with distributions.
    Lists all proposals with their student.

    :param proposals:
    :return:
    """
    wb = Workbook()

    # grab the active worksheet
    ws = wb.active
    ws.title = "distributions"

    ws['A1'] = "Proposals with students and staff from {}".format(settings.NAME_PRETTY)
    ws['A1'].style = 'Headline 2'
    ws['F1'] = "Exported on: " + str(datetime.now())

    header = ["Title", "Track", "Research group", "Responsible", "Assistants", "Chosen", "Student Emails",
              "Staff Emails"]

    ws.column_dimensions['A'].width = 25  # title
    ws.column_dimensions['D'].width = 25  # responsible
    ws.column_dimensions['E'].width = 25  # assistants
    ws.column_dimensions['F'].width = 25  # chosen
    ws.column_dimensions['G'].width = 25  # student mail
    ws.column_dimensions['H'].width = 25  # staff mail

    ws.append(header)
    for col in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']:
        ws[col + '2'].style = 'Headline 3'

    for p in proposals:
        des = p.distributions.filter(TimeSlot=get_timeslot())
        row = [p.Title, p.Track.__str__(), p.Group.__str__(),
               p.ResponsibleStaff.usermeta.get_nice_name()]
        assistants = ''
        for a in p.Assistants.all():
            assistants += a.usermeta.get_nice_name() + "; "
        row.append(assistants)
        stds = ''
        stdsmail = ''
        for d in des:
            stdsmail += d.Student.email + '; '
            try:
                stds += d.Student.usermeta.get_nice_fullname() + " (" + d.Student.usermeta.Studentnumber + "); "
            except:
                stds += d.Student.usermeta.get_nice_fullname() + "; "
        row.append(stds)
        row.append(stdsmail)
        emails = '{};'.format(p.ResponsibleStaff.email)
        for a in p.Assistants.all():
            emails += '{};'.format(a.email)
        row.append(emails)
        # row[4].alignment = Alignment(wrapText=True)
        # row[5].alignment = Alignment(wrapText=True)
        ws.append(row)
    return save_virtual_workbook(wb)


