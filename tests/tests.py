import datetime
import django
from django.conf import settings
from django.test import TestCase
from tests.models import Sample
import tables_cleaner

NUM_RECORDS = 100



class BaseTestCase(TestCase):

    #fixtures = [os.path.join(FIXTURES_DIR, 'workflows.json'), ]

    def setUp(self):
        self.populateModels()

    def tearDown(self):
        pass

    def populateModels(self):
        now = datetime.datetime.now().date()
        for i in range(NUM_RECORDS):
            Sample.objects.create(
                created=now - datetime.timedelta(days=i)
            )


class SimpleTestCase(BaseTestCase):

    def test_clean_tables_from_settings(self):

        # Retrieve table prescriptions from settings
        table = settings.TABLES_CLEANER_TABLES[0]
        self.assertEqual(table['model_name'], 'tests.sample')
        to_keep = max(table['keep_records'], table['keep_since_days'])

        # Squeeze table
        self.assertEqual(NUM_RECORDS, Sample.objects.count())
        tables_cleaner.clean_tables()
        self.assertEqual(min(to_keep, NUM_RECORDS), Sample.objects.count())

    def run_clean_table(self, table_settings, expected_removed_count):
        expected_left_count = Sample.objects.count() - expected_removed_count
        n = tables_cleaner.clean_table(**table_settings)
        self.assertEqual(expected_removed_count, n)
        self.assertEqual(expected_left_count, Sample.objects.count())

    def test_remove_all(self):
        self.run_clean_table(
            table_settings={'model_name': 'tests.sample', 'keep_records': 0, 'keep_since_days': 0, 'keep_since_hours': 0, },
            expected_removed_count=NUM_RECORDS,
        )

    def test_keep_one(self):
        self.run_clean_table(
            table_settings={'model_name': 'tests.sample', 'keep_records': 1, 'keep_since_days': 0, 'keep_since_hours': 0, },
            expected_removed_count=NUM_RECORDS - 1,
        )

    def test_keep_some(self):
        n = int(NUM_RECORDS / 10)
        self.run_clean_table(
            table_settings={'model_name': 'tests.sample', 'keep_records': n, 'keep_since_days': 0, 'keep_since_hours': 0, },
            expected_removed_count=NUM_RECORDS - n,
        )

    def test_keep_all(self):
        self.run_clean_table(
            table_settings={'model_name': 'tests.sample', 'keep_records': NUM_RECORDS, 'keep_since_days': 0, 'keep_since_hours': 0, },
            expected_removed_count=0,
        )

    def run_clean_table_by_days(self, days):
        self.assertTrue(days <= NUM_RECORDS)
        today = datetime.datetime.now().date()
        table_settings={'model_name': 'tests.sample', 'keep_records': 0, 'keep_since_days': days, 'keep_since_hours': 0, }
        self.run_clean_table(
            table_settings=table_settings,
            expected_removed_count=NUM_RECORDS - days,
        )
        oldest = Sample.objects.order_by('created').first().created.date()
        self.assertEqual((today - oldest).days, days - 1)

    def test_keep_today(self):
        self.run_clean_table_by_days(1)

    def test_keep_last_week(self):
        self.run_clean_table_by_days(7)

    def test_keep_all_by_days(self):
        self.run_clean_table_by_days(NUM_RECORDS)

    def test_keep_too_much_by_days(self):
        days = NUM_RECORDS + 1
        self.run_clean_table(
            table_settings={'model_name': 'tests.sample', 'keep_records': 0, 'keep_since_days': days, 'keep_since_hours': 0, },
            expected_removed_count=0,
        )

    def test_mixed_1(self):
        self.run_clean_table(
            table_settings={'model_name': 'tests.sample', 'keep_records': 10, 'keep_since_days': 10, 'keep_since_hours': 0, },
            expected_removed_count=NUM_RECORDS - 10,
        )

    def test_mixed_2(self):
        self.run_clean_table(
            table_settings={'model_name': 'tests.sample', 'keep_records': 10, 'keep_since_days': 20, 'keep_since_hours': 0, },
            expected_removed_count=NUM_RECORDS - 20,
        )

    def test_mixed_3(self):
        self.run_clean_table(
            table_settings={'model_name': 'tests.sample', 'keep_records': 20, 'keep_since_days': 10, 'keep_since_hours': 0, },
            expected_removed_count=NUM_RECORDS - 20,
        )
