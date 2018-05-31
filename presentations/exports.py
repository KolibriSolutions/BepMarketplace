from django.utils import timezone
from openpyxl import Workbook
from openpyxl.writer.excel import save_virtual_workbook

from general_view import timestamp, get_name


def listPresentationsXls(sets):
    """
    Lists the presentations planning with a set on each tab. Same formatting as before marketplace

    :param sets:
    :return:
    """
    codeExt = "5XED0"
    codeBEP = "5XEC0"
    wb = Workbook()
    wb.remove_sheet(wb.active)
    wss = []
    for pset in sets:
        tit = str(pset.id) + " (" + pset.Track.Name + ")"
        ws = wb.create_sheet(title=tit)
        wss.append(ws)
        ws['C1'] = timezone.localtime(pset.DateTime).date().strftime("%A %d %B %Y")
        ws['C3'] = "Track: " + pset.Track.Name
        ws['C4'] = "Track responsible staff: " + get_name(pset.Track.Head)
        ws['C5'] = "Exported on: " + timestamp()
        ws['C6'] = "Presentation room: " + pset.PresentationRoom.Name
        ws['C7'] = "Assessment room: " + pset.AssessmentRoom.Name
        assessors = ''
        for a in pset.Assessors.all():
            assessors += get_name(a) + "; "
        ws['C8'] = 'Assessors: ' + assessors[:-2]
        ws['C9'] = ''

        ws['C1'].style = 'Headline 2'
        # courses span two columns
        ws['G9'] = 'Courses'
        ws.merge_cells('G9:H9')
        ws['G9'].style = 'Headline 3'
        ws['H9'].style = 'Headline 3'
        # custom dimensions
        ws.column_dimensions['C'].width = 25  # std name
        ws.column_dimensions['E'].width = 25  # responsible name
        ws.column_dimensions['F'].width = 25  # assistants
        ws.column_dimensions['G'].width = 6  # codeBEP
        ws.column_dimensions['H'].width = 6  # codeExt
        ws.column_dimensions['I'].width = 50  # project name

        header = ["Type", "Stud. id", "Name", "First name", "Responsible teacher", "Assistants",
                  codeBEP, codeExt, "Project", "Time", "Duration"]
        ws.append(header)
        for col in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K']:
            ws[col + '10'].style = 'Headline 3'

        for slot in pset.timeslots.all():
            if slot.CustomType:
                row = [slot.get_CustomType_display(), '', '', '', '', '', '', '', '']
            else:
                d = slot.Distribution
                row = ['', d.Student.usermeta.Studentnumber, d.Student.usermeta.Fullname, d.Student.first_name,
                       get_name(d.Proposal.ResponsibleStaff)]
                assistants = ''
                for a in d.Proposal.Assistants.all():
                    assistants += get_name(a) + "; "
                row.append(assistants[:-2])
                row.append('x' if d.Student.usermeta.EnrolledBEP else '')
                row.append('x' if d.Student.usermeta.EnrolledExt else '')
                row.append(d.Proposal.Title)
            row.append(timezone.localtime(slot.DateTime).time().strftime("%H:%M"))
            row.append(slot.Duration())
            ws.append(row)
    return save_virtual_workbook(wb)
