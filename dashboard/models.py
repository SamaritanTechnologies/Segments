from django.db import models
from django.db.models import Sum
from django.urls import reverse

from accounts.models import User


class Audience(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    prompt = models.TextField()
    email = models.EmailField(null=True, blank=True)
    process_completed = models.BooleanField(default=False)


class Segment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    sample_size = models.IntegerField(null=True, blank=True)

    def traits(self):
        return self.traits_set.all()

    def traits_comma(self):
        return ', '.join(trait.title for trait in self.traits_set.all())

    @property
    def percentage_division(self):
        if self.sample_size:
            total_sample_size = Segment.objects.filter(user=self.user).aggregate(total=Sum('sample_size'))['total']
            if total_sample_size == 0:
                return 'N/A'

            return f"{(self.sample_size / total_sample_size) * 100:.2f}%"
        else:
            return 0

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


class Questions(models.Model):
    audience = models.ForeignKey(Audience, on_delete=models.CASCADE, null=True, blank=True)
    question = models.TextField()

    def __str__(self):
        return self.question


class Answers(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    answer = models.TextField()

    def __str__(self):
        return self.answer


class AnalyzeReport(models.Model):
    segment = models.ForeignKey(Segment, on_delete=models.CASCADE, null=True, blank=True)
    audience = models.ForeignKey(Audience, on_delete=models.CASCADE)
    trait = models.CharField(max_length=50)
    question = models.ManyToManyField(Questions, null=True, blank=True)
    answer = models.ManyToManyField(Answers, null=True, blank=True)
    loop = models.BooleanField(default=False)

    def __str__(self):
        return self.trait
