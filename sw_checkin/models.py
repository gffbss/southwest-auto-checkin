from datetime import timedelta, datetime

from django.db import models
from django.db.models.signals import post_save

from sw_checkin import tasks


class Passenger(models.Model):
    """Passenger to be checked in."""
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()

    def __unicode__(self):
        return u'%s %s' % (self.first_name, self.last_name)


class Reservation(models.Model):
    """Flight reservation information."""
    passenger = models.ForeignKey(Passenger)
    confirmation_num = models.CharField(max_length=13)
    flight_time = models.TimeField()
    flight_date = models.DateField()
    success = models.BooleanField(default=False)

    def __unicode__(self):
        return u'%s: %s' % (self.passenger, self.flight_date)


def reservation_post_save(sender, instance, **kwargs):
    checkin_time = datetime.combine(
        (instance.flight_date - timedelta(days=1)),  # Subtract 24 hours for checkin time
        instance.flight_time
    )
    checkin_time += timedelta(hours=7)  # Add 7 hours for UTC, start a minute early
    checkin_time -= timedelta(seconds=30)  # Start trying 30 seconds
    tasks.checkin_job.apply_async(args=[instance], eta=checkin_time)
    # tasks.checkin_job(instance)

post_save.connect(reservation_post_save, sender=Reservation, dispatch_uid="reservation_post_save")