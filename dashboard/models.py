from django.db import models


# Create your models here.
from django.urls import reverse


class Segment(models.Model):
    sample_size = models.IntegerField(null=True, blank=True)

    def traits(self):
        return self.traits_set.all()

    def __str__(self):
        return str(self.sample_size)

    def delete_url(self):
        return reverse('delete_segment', args=[self.pk])


class Traits(models.Model):
    title = models.CharField(max_length=50)
    segment = models.ForeignKey(Segment, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = "Traits"
