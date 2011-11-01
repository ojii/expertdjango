# -*- coding: utf-8 -*-
#!/usr/bin/env python
import os
import sys

urlpatterns = []

INSTALLED_APPS = [
    'expertdjango',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

MIDDLEWARE_CLASSES = ['expertdjango.expertmiddleware']

ROOT_URLCONF = 'runtests'

def run_tests():
    from django.conf import settings
    settings.configure(
        INSTALLED_APPS = INSTALLED_APPS,
        ROOT_URLCONF = ROOT_URLCONF,
        DATABASES = DATABASES,
        MIDDLEWARE_CLASSES = MIDDLEWARE_CLASSES,
    )

    # Run the test suite, including the extra validation tests.
    from django.test.utils import get_runner
    TestRunner = get_runner(settings)
    
    test_runner = TestRunner(verbosity=1, interactive=False, failfast=False)
    failures = test_runner.run_tests(['expertdjango'])
    return failures

if __name__ == "__main__":
    failures = run_tests()
    if failures:
        sys.exit(bool(failures))
