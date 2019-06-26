from django.db import models

class AccessGrant(models.Model):
    LevelOptions = (
        (1, 'Type1'),
        (2, 'Type2')
    )

    Email = models.EmailField()
    Level = models.IntegerField(choices=LevelOptions, default=1)

    def __str__(self):
        return "{} for level {}".format(self.Email, self.Level)

