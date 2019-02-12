from django.core.cache import cache
import csv
import logging

logger = logging.getLogger('django')

class osirisPerson:
    def __init__(self, csvline):
        self.email = csvline[0]
        self.idnumber = csvline[1]
        self.cohort = csvline[2]
        self.ects = csvline[3]
        if csvline[4] == 'yes' or csvline[4] == '1' or csvline[4] == 1:
            self.automotive = True
        else:
            self.automotive = False


class osirisData:
    # TODO remove hardcoded file
    FILE = 'osiris.csv'

    def __init__(self):
        self.data = cache.get('osirisdata')
        if self.data is None:
            self._readdata()
            cache.set('osirisdata', self.data, 24*60*60)

    def _readdata(self):
        self.data = {}
        with open(self.FILE, 'r') as stream:
            csvreader = csv.reader(stream, delimiter=';', quotechar='"')
            for i, data in enumerate(csvreader):
                if i == 0:
                    continue #skip first line (headers)
                try:
                    self.data[data[0]] = osirisPerson(data)
                except:
                    logger.error("Invalid csv in osiris csv on line {}".format(i))
                    continue

    def get(self, email):
        try:
            return self.data[email]
        except KeyError:
            return None

    def getall(self, email=None, enrolled=None, extension=None, cohort=None):
        data = []
        for e, person in self.data.items():
            if enrolled is not None:
                if person.enrolled == enrolled:
                    data.append(person)
            if extension is not None:
                if person.extension == extension:
                    data.append(person)
            if cohort is not None:
                if person.cohort == cohort:
                    data.append(person)
            if email is not None:
                if email in e or e in email:
                    data.append(person)
        return data

    def getalldata(self):
        return list(self.data.values())

    def getallEmail(self):
        return list(self.data.keys())
