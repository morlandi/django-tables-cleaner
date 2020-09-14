import datetime
from django.utils import timezone
from django.core.management.base import BaseCommand
from project.models import Sample


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('num_samples', type=int)

    def handle(self, *args, **options):
        n = options.get('num_samples')
        now = timezone.now()
        for i in range(n):
            Sample.objects.create(
                created=now - datetime.timedelta(days=i)
            )

        print('%d samples created. Total samples now: %d' % (n, Sample.objects.count()))
