from django.db import models
from django.core.exceptions import ValidationError
from datetime import datetime

class Rate(models.Model):
    standard_rate_begin = models.TimeField()
    standard_rate_end = models.TimeField()
    standard_standing_charge = models.IntegerField()
    standard_minute_charge = models.IntegerField()
    
    reduced_rate_begin = models.TimeField()
    reduced_rate_end = models.TimeField()
    reduced_standing_charge = models.IntegerField()
    reduced_minute_charge = models.IntegerField()

    def __validate_rate_intervals(self):
        dt_standard_rate_begin = datetime.strptime(
            self.standard_rate_begin,
            '%H:%M'
        )

        dt_standard_rate_end = datetime.strptime(
            self.standard_rate_end,
            '%H:%M'
        )

        dt_reduced_rate_begin = datetime.strptime(
            self.reduced_rate_begin,
            '%H:%M'
        )

        dt_reduced_rate_end = datetime.strptime(
            self.reduced_rate_end,
            '%H:%M'
        )

        standard_rate_duration = dt_standard_rate_end - dt_standard_rate_begin
        reduced_rate_duration = dt_reduced_rate_end - dt_reduced_rate_begin

        standard_rate_seconds = standard_rate_duration.seconds
        reduced_rate_seconds = reduced_rate_duration.seconds

        total_seconds = standard_rate_seconds + reduced_rate_seconds

        if total_seconds != 86400:
            raise ValidationError(
                'The some of date rate periods does not last 24hrs')

    def save(self, *args, **kwargs):
        self.__validate_rate_intervals()
        return super().save(*args, **kwargs)