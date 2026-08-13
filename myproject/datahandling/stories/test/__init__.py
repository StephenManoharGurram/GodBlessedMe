"""
stories/tests/__init__.py

Test suite for the stories application.

This directory contains comprehensive tests for:
- Validators (test_validators.py)
- Services (test_services.py)
- API Views (test_views.py)

Test Coverage:
- Input validation for all fields
- Service layer business logic
- API endpoint behavior
- Error handling and responses
- Edge cases and integration scenarios

To run all tests:
    python manage.py test stories

To run specific test file:
    python manage.py test stories.tests.test_validators
    python manage.py test stories.tests.test_services
    python manage.py test stories.tests.test_views

To run specific test class:
    python manage.py test stories.tests.test_validators.FieldValidatorEmailTests

To run specific test method:
    python manage.py test stories.tests.test_validators.FieldValidatorEmailTests.test_valid_email

To run with verbosity:
    python manage.py test stories -v 2

To run with coverage report:
    pip install coverage
    coverage run --source='stories' manage.py test stories
    coverage report
"""