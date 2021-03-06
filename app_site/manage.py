#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app_site.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError:
        # The above import may fail for some other reason. Ensure that the
        # issue is really that Django is missing to avoid masking other
        # exceptions on Python 2.
        try:
            import django
        except ImportError:
            raise ImportError(
                "Couldn't import Django. Are you sure it's installed and "
                "available on your PYTHONPATH environment variable? Did you "
                "forget to activate a virtual environment?"
            )
        raise

    is_testing = 'tests' in sys.argv
    if is_testing:
        import coverage
        cov = coverage.coverage(source=['streaming'], omit=['*/tests/*', 'streaming/migrations/*', 'streaming/management/*', '*/__init__.py', 'streaming/admin.py', 'streaming/tests.py'])
        #cov.set_option('report:show_missing', True)
        cov.set_option("run:branch", True)
        cov.erase()
        cov.start()
    execute_from_command_line(sys.argv)
    if is_testing:
        cov.stop()
        cov.save()
        cov.html_report(directory='covhtml')
        cov.report()
