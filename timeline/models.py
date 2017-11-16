from django.core.exceptions import ValidationError
from django.db import models

class TimeSlot(models.Model):
    """
    A timeslot is a year in which the current BEP runs. It consists of multiple timephases.
    """
    Name = models.CharField(max_length=250)
    Begin = models.DateField()
    End = models.DateField()

    def __str__(self):
        return self.Name

    def clean(self):
        if self.Begin > self.End:
            raise ValidationError("End date should be larger than begin date")

    class Meta:
        ordering = ["Begin"]


class TimePhase(models.Model):
    """
    A timephase is a phase the system is in. Each phase has its own pages and permissions.
    """
    Types = (
        (1, "Generating project proposals"),
        (2, "Projects quality check"),
        (3, "Students choosing projects"),
        (4, "Distribution of projects"),
        (5, "Gather and process objections"),
        (6, "Execution of the projects"),
        (7, "Presentation of results"),
    )

    Description = models.IntegerField(choices=Types)
    Begin = models.DateField()
    End = models.DateField()
    CountdownEnd = models.DateField(null=True, blank=True)
    Timeslot = models.ForeignKey(TimeSlot, on_delete=models.PROTECT, related_name="timephases")

    def __str__(self):
        return self.Types[self.Description - 1][1] + " in " + str(self.Timeslot)

    def clean(self):
        if self.Begin > self.End:
            raise ValidationError("End date should be larger than begin date")
        if not (self.Timeslot.Begin <= self.Begin <= self.Timeslot.End):
            raise ValidationError("Begin date should be in timeslot {}".format(self.Timeslot))
        if not (self.Timeslot.Begin <= self.End <= self.Timeslot.End):
            raise ValidationError("End date should be in timeslot {}".format(self.Timeslot))
        if self.Timeslot.timephases.filter(Description=self.Description).exists():
            if self.Timeslot.timephases.get(Description=self.Description) != self:
                raise ValidationError("Timeslot {} already has timephase {}".format(self.Timeslot, self.Description))

    class Meta:
        ordering = ['Timeslot', 'Begin']