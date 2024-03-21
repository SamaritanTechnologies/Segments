from django.db.models.signals import post_save
from django.dispatch import receiver
from django_celery_beat.models import IntervalSchedule
from .models import Audience


@receiver(post_save, sender=Audience)
def create_or_update_periodic_task(sender, instance, created, **kwargs):
    if created:
        interval = instance.create_interval()
        instance.setup_task(interval)
    else:
        if instance.task is not None:
            interval = instance.task.interval
            interval_schedule = IntervalSchedule.objects.get(id=interval.id)
            interval_schedule.every = 1
            interval_schedule.save()
            instance.task.enabled = True
            instance.task.save()
