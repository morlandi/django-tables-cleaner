from django.db import models


class Sample(models.Model):

    created = models.DateTimeField('created', null=True, blank=True, )

    class Meta:
        ordering = ('-created', )  # better choice for UI
        get_latest_by = "-created"

    def __str__(self):
        return '%d (%s)' % (self.id, str(self.created))
