from django.core.management.base import BaseCommand, CommandError
from streaming.models import *


class Command(BaseCommand):
    def handle(self, *args, **options):
        g = SiteUser.objects.get(username='GavinDaGOAT')
        g.billing.cc_num = 1936
        g.billing.save()
        g.save()
