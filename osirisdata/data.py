#  Bep Marketplace ELE
#  Copyright (c) 2016-2022 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
from openpyxl import load_workbook

from osirisdata.models import OsirisDataFile


class osirisPerson:
    def __init__(self, csvline):
        self.email = csvline[0].value
        self.idnumber = int(csvline[1].value)
        self.cohort = int(csvline[2].value)
        # ects:
        if type(csvline[3].value) == int:
            self.ects = csvline[3].value
        elif type(csvline[3].value) == float:
            self.ects = int(round(csvline[3].value))
        else:  # assume string, could contain half points
            self.ects = int(round(float(csvline[3].value.replace(',', '.'))))
        # automotive
        if type(csvline[4].value) == str:
            if csvline[4].value == 'yes' or csvline[4].value == '1' or csvline[4].value.lower() == 'bau' or csvline[4].value.lower() == 'au':
                self.automotive = True
            else:
                self.automotive = False
        else:
            self.automotive = bool(csvline[4].value)


def read_osiris_xlsx():
    try:
        file = OsirisDataFile.objects.last().File
    except:
        raise Exception('File not found')
    wb = load_workbook(filename=file, read_only=True)
    ws = wb.active
    rows = list(ws.rows)
    data = []
    header = [x.value for x in rows[0]]
    log = []
    for row in rows[1:]:
        try:
            data.append(osirisPerson(row[0:5]))
        except:
            log.append('row: {0} failed'.format([cell.value for cell in row[0:5]]))
    return data, log


#
#
# class osirisData:
#     # FILE = 'osiris.csv'
#     # Could be changed to some timeslot or file chooser, but for now the latest uploaded file:
#     try:
#         FILE = OsirisDataFile.objects.last().File
#     except:
#         FILE = None
#
#     def __init__(self):
#         # self.data = cache.get('osirisdata')
#         # if self.data is None:
#         self.data = None
#         self.log = None
#         self._readdata()
#
#     #     cache.set('osirisdata', self.data, 24 * 60 * 60)
#     #     self.data = None
#
#     def _readdata(self):
#         log_str = []
#         self.data = {}
#         with open(self.FILE, 'r') as stream:
#             csvreader = csv.reader(stream, delimiter=';', quotechar='"')
#             for i, data in enumerate(csvreader):
#                 if i == 0:
#                     continue  # skip first line (headers)
#                 try:
#                     self.data[data[0]] = osirisPerson(data)
#                 except Exception as e:
#                     logger.error("Invalid csv in osiris csv on line {}. Error {}".format(i, e))
#                     log_str.append("Invalid csv in osiris csv on line {}. Error {}".format(i, e))
#                     continue
#         self.log= log_str
#
#     def get(self, email):
#         try:
#             return self.data[email]
#         except KeyError:
#             return None
#
#     def getall(self, email=None, enrolled=None, extension=None, cohort=None):
#         data = []
#         for e, person in self.data.items():
#             if enrolled is not None:
#                 if person.enrolled == enrolled:
#                     data.append(person)
#             if extension is not None:
#                 if person.extension == extension:
#                     data.append(person)
#             if cohort is not None:
#                 if person.cohort == cohort:
#                     data.append(person)
#             if email is not None:
#                 if email in e or e in email:
#                     data.append(person)
#         return data
#
#     def getalldata(self):
#         return list(self.data.values())
#
#     def getallEmail(self):
#         return list(self.data.keys())
