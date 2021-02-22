from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from rates.models import Rate
from datetime import datetime
from math import floor
import dateutil.parser
import ipdb


class CallRecord(models.Model):
    call_id = models.IntegerField(unique=True)
    source = models.IntegerField()
    destination = models.IntegerField()
    start_timestamp = models.DateTimeField(default=timezone.now)
    end_timestamp = models.DateTimeField(null=True)
    rate = models.ForeignKey(Rate, on_delete=models.PROTECT)

    def save(self, *args, **kwargs):
        self.__validate_end_timestamp()
        
        return super().save(*args, **kwargs)

    def __validate_end_timestamp(self):
        if self.end_timestamp:
            end_timestamp = dateutil.parser.isoparse(self.end_timestamp)
            
            if end_timestamp < self.start_timestamp:
                raise ValidationError('end_timestamp cannot happen before start_timestamp')

    def __calculate_starting_rate_type(self):
        call_start_date = self.start_timestamp.date()

        dt_standard_rate_begin = datetime.combine(
            call_start_date, self.rate.standard_rate_begin
        ).replace(tzinfo=timezone.get_default_timezone())

        dt_starndard_rate_end = datetime.combine(
            call_start_date, self.rate.standard_rate_end
        ).replace(tzinfo=timezone.get_default_timezone())

        standard_rate_delta = dt_starndard_rate_end - dt_standard_rate_begin

        if standard_rate_delta == -1:
            dt_starndard_rate_end = dt_starndard_rate_end + timedelta(days=1)

        if dt_standard_rate_begin <= self.start_timestamp < dt_starndard_rate_end:
            return 'standard'
        else:
            return 'reduced'


    def calculate_call_cost(self):
        total = 0
        call_timedelta = dateutil.parser.isoparse(self.end_timestamp) - self.start_timestamp
        call_seconds = floor(call_timedelta.total_seconds())
        

        beginning_rate_type = self.__calculate_starting_rate_type()
        rate = beginning_rate_type

        if rate == 'standard':
            total += self.rate.standard_standing_charge

        else:
            total += self.rate.reduced_standing_charge

        current_date = self.start_timestamp.date()
        point_in_time = self.start_timestamp.time()

        while call_seconds > 0:
            if rate == 'standard':
                delta_until_rate_switch = datetime.combine(
                    current_date,
                    self.rate.standard_rate_end
                ) - datetime.combine(
                    current_date,
                    point_in_time
                )

                seconds_until_rate_switch = delta_until_rate_switch.seconds

                if seconds_until_rate_switch < call_seconds:
                    minutes = seconds_until_rate_switch // 60

                    total += minutes * self.rate.standard_minute_charge

                else:
                    minutes = call_seconds // 60
                    total += minutes * self.rate.standard_minute_charge

                call_seconds -= seconds_until_rate_switch
                rate = 'reduced'
                point_in_time = self.rate.standard_rate_end

            else:
                delta_until_rate_switch = datetime.combine(
                    current_date,
                    self.rate.reduced_rate_end
                ) - datetime.combine(
                    current_date,
                    point_in_time
                )

                seconds_until_rate_switch = delta_until_rate_switch.seconds

                if seconds_until_rate_switch < call_seconds:
                    minutes = seconds_until_rate_switch // 60

                    total += minutes * self.rate.reduced_minute_charge

                else:
                    minutes = call_seconds // 60
                    total += minutes * self.rate.reduced_minute_charge

                call_seconds -= seconds_until_rate_switch
                rate = 'standard'
                point_in_time = self.rate.standard_rate_begin
        
        
        return total