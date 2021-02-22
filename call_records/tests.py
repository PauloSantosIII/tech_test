from django.test import TestCase
from django.db import IntegrityError
from rates.models import Rate
from call_records.models import CallRecord
import dateutil.parser

class TestCallRecordModel(TestCase):
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

        Rate.objects.create(**self.rate_data)
        self.rate = Rate.objects.first()

        self.call_record_data = {
            'source': 99988526423,
            'destination': 9993468278,
            'call_id': 71
        }

        self.start_timestamp = '2017-12-12T15:07:13Z'
        self.end_timestamp = '2017-12-12T15:14:56Z'
        self.call_cost = 7 * self.rate_data['standard_minute_charge'] + self.rate_data['standard_standing_charge']

        self.call_record_data_2 = {
            'source': 99988526423,
            'destination': 9993468278,
            'call_id': 75
        }

        self.start_timestamp_2 = '2017-12-12T21:57:13Z'
        self.end_timestamp_2 = '2017-12-13T22:10:56Z'
        self.call_cost_2 = 8694 # * self.rate_data['standard_minute_charge'] + self.rate_data['standard_standing_charge']

    def test_call_record_create(self):
        CallRecord.objects.create(
            **self.call_record_data,
            start_timestamp=self.start_timestamp,
            rate=self.rate
        )

        call_record = CallRecord.objects.last()

        self.assertDictContainsSubset(self.call_record_data, call_record.__dict__)

        self.assertEqual(
            call_record.start_timestamp,
            dateutil.parser.isoparse(self.start_timestamp)
        )

        self.assertEqual(call_record.end_timestamp, None)

        self.assertEqual(call_record.rate, self.rate)

    def test_call_id_field_is_unique(self):
        CallRecord.objects.create(
            **self.call_record_data,
            start_timestamp=self.start_timestamp,
            rate=self.rate
        )

        with self.assertRaises(IntegrityError):
            CallRecord.objects.create(
                **self.call_record_data,
                start_timestamp=self.start_timestamp,
                rate=self.rate
            )

    def test_update_call_record(self):
        CallRecord.objects.create(
            **self.call_record_data,
            start_timestamp=self.start_timestamp,
            rate=self.rate
        )

        call_record = CallRecord.objects.get(
            call_id=self.call_record_data['call_id']
        )

        call_record.end_timestamp = self.end_timestamp
        call_record.save()

        self.assertDictContainsSubset(self.call_record_data, call_record.__dict__)

        self.assertEqual(
            call_record.start_timestamp,
            dateutil.parser.isoparse(self.start_timestamp)
        )

        self.assertEqual(call_record.end_timestamp, self.end_timestamp)

        self.assertEqual(call_record.rate, self.rate)

    def test_calculate_basic_call_cost(self):
        CallRecord.objects.create(
            **self.call_record_data,
            start_timestamp=self.start_timestamp,
            rate=self.rate
        )

        call_record = CallRecord.objects.get(
            call_id=self.call_record_data['call_id']
        )

        call_record.end_timestamp = self.end_timestamp
        call_record.save()

        self.assertDictContainsSubset(self.call_record_data, call_record.__dict__)

        self.assertEqual(
            call_record.start_timestamp,
            dateutil.parser.isoparse(self.start_timestamp)
        )

        self.assertEqual(call_record.end_timestamp, self.end_timestamp)

        self.assertEqual(call_record.rate, self.rate)

        call_cost = call_record.calculate_call_cost()
        self.assertEqual(call_cost, self.call_cost)

    def test_calculate_basic_call_cost_edge_case(self):
        CallRecord.objects.create(
            **self.call_record_data,
            start_timestamp=self.start_timestamp_2,
            rate=self.rate
        )

        call_record = CallRecord.objects.get(
            call_id=self.call_record_data['call_id']
        )

        call_record.end_timestamp = self.end_timestamp_2
        call_record.save()

        self.assertDictContainsSubset(self.call_record_data, call_record.__dict__)

        self.assertEqual(
            call_record.start_timestamp,
            dateutil.parser.isoparse(self.start_timestamp_2)
        )

        self.assertEqual(call_record.end_timestamp, self.end_timestamp_2)

        self.assertEqual(call_record.rate, self.rate)

        call_cost = call_record.calculate_call_cost()
        self.assertEqual(call_cost, self.call_cost_2)