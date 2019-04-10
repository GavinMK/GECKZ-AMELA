from django.core.management.base import BaseCommand, CommandError
from streaming.models import *
from datetime import *


class Command(BaseCommand):
    def handle(self, *args, **options):
        for billing in Billing.objects.all():
            if billing.next_payment_date <= datetime.now().date():
                billing.charge()
