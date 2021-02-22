from django.test import TestCase
from django.core.exceptions import ValidationError
from rates.models import Rate
from datetime import datetime

class TestRateModel(TestCase):
    def setUp(self):
        self.rate_data = {
            'standard_rate_begin': '6:00',
            'standard_rate_end': '22:00',
            'standard_standing_charge': 36,
            'standard_minute_charge': 9,
            'reduced_rate_begin': '22:00',
            'reduced_rate_end': '6:00',
            'reduced_standing_charge': 36,
            'reduced_minute_charge': 0,
        }

        self.converted_rate_data = {
            'standard_rate_begin': datetime.strptime('6:00', '%H:%M').time(),
            'standard_rate_end': datetime.strptime('22:00', '%H:%M').time(),
            'standard_standing_charge': 36,
            'standard_minute_charge': 9,
            'reduced_rate_begin': datetime.strptime('22:00', '%H:%M').time(),
            'reduced_rate_end': datetime.strptime('6:00', '%H:%M').time(),
            'reduced_standing_charge': 36,
            'reduced_minute_charge': 0,
        }

        # fare periods must be covered 24 hours
        self.invalid_rate_data = {
            'standard_rate_begin': '6:01',
            'standard_rate_end': '22:00',
            'standard_standing_charge': 36,
            'standard_minute_charge': 9,
            'reduced_rate_begin': '22:00',
            'reduced_rate_end': '6:00',
            'reduced_standing_charge': 36,
            'reduced_minute_charge': 0,
        }

    def test_create_valid_rate(self):
        # create
        rate  = Rate.objects.create(**self.rate_data)

        #load
        rate  = Rate.objects.last()

        self.assertDictContainsSubset(self.converted_rate_data, rate.__dict__)

    def test_validation_error_for_invalid_rate_intervals(self):
        with self.assertRaises(ValidationError):
            rate = Rate.objects.create(**self.invalid_rate_data)