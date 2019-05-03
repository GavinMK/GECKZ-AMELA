from django.core.management.base import BaseCommand, CommandError
from streaming.tests import *


class Command(BaseCommand):
    def handle(self, *args, **options):
        test1 = SimpleTest()
        test1.setUp()
        public_method_names = [method for method in dir(test1) if callable(getattr(test1, method)) if method.startswith('test_')]
        for method in public_method_names:
            getattr(test1, method)()  # call
