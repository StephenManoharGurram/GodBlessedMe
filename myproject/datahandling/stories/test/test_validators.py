"""
stories/tests/test_validators.py

Test suite for input validators.
Tests: email, name, phone, title, story content validation.
"""

from django.test import TestCase
from stories.validator import (
    FieldValidator,
    ValidationError,
    ValidationErrorList,
    validate_story_submission
)


class FieldValidatorEmailTests(TestCase):
    """Test email validation"""
    
    def test_valid_email(self):
        """Valid email should pass"""
        email = FieldValidator.validate_email('john@gmail.com')
        self.assertEqual(email, 'john@gmail.com')
    
    def test_email_lowercase_conversion(self):
        """Email should be converted to lowercase"""
        email = FieldValidator.validate_email('JOHN@GMAIL.COM')
        self.assertEqual(email, 'john@gmail.com')
    
    def test_email_with_whitespace_stripped(self):
        """Email should have whitespace stripped"""
        email = FieldValidator.validate_email('  john@gmail.com  ')
        self.assertEqual(email, 'john@gmail.com')
    
    def test_empty_email_raises_error(self):
        """Empty email should raise error"""
        with self.assertRaises(ValidationError) as cm:
            FieldValidator.validate_email('')
        self.assertEqual(cm.exception.message, "Email is required")
    
    def test_invalid_email_format(self):
        """Invalid email format should raise error"""
        with self.assertRaises(ValidationError) as cm:
            FieldValidator.validate_email('invalid-email')
        self.assertEqual(cm.exception.message, "Invalid email format")
    
    def test_email_no_at_symbol(self):
        """Email without @ should raise error"""
        with self.assertRaises(ValidationError):
            FieldValidator.validate_email('invalidgmail.com')
    
    def test_email_no_domain(self):
        """Email without domain should raise error"""
        with self.assertRaises(ValidationError):
            FieldValidator.validate_email('john@')
    
    def test_email_too_long(self):
        """Email longer than 254 chars should raise error"""
        long_email = 'a' * 250 + '@test.com'
        with self.assertRaises(ValidationError) as cm:
            FieldValidator.validate_email(long_email)
        self.assertIn("too long", cm.exception.message)
    
    def test_email_with_plus_sign(self):
        """Email with plus sign should be valid"""
        email = FieldValidator.validate_email('john+tag@gmail.com')
        self.assertEqual(email, 'john+tag@gmail.com')


class FieldValidatorNameTests(TestCase):
    """Test name validation"""
    
    def test_valid_first_name(self):
        """Valid first name should pass"""
        name = FieldValidator.validate_name('John', 'First Name')
        self.assertEqual(name, 'John')
    
    def test_valid_last_name(self):
        """Valid last name should pass"""
        name = FieldValidator.validate_name('Doe', 'Last Name')
        self.assertEqual(name, 'Doe')
    
    def test_name_with_hyphen(self):
        """Name with hyphen should pass"""
        name = FieldValidator.validate_name('Mary-Jane', 'First Name')
        self.assertEqual(name, 'Mary-Jane')
    
    def test_name_with_apostrophe(self):
        """Name with apostrophe should pass"""
        name = FieldValidator.validate_name("O'Brien", 'Last Name')
        self.assertEqual(name, "O'Brien")
    
    def test_name_with_spaces(self):
        """Name with spaces should pass"""
        name = FieldValidator.validate_name('Jean Pierre', 'First Name')
        self.assertEqual(name, 'Jean Pierre')
    
    def test_empty_name_raises_error(self):
        """Empty name should raise error"""
        with self.assertRaises(ValidationError) as cm:
            FieldValidator.validate_name('', 'First Name')
        self.assertEqual(cm.exception.message, "First Name is required")
    
    def test_name_too_short(self):
        """Name with only 1 character should raise error"""
        with self.assertRaises(ValidationError) as cm:
            FieldValidator.validate_name('A', 'First Name')
        self.assertIn("at least 2 characters", cm.exception.message)
    
    def test_name_too_long(self):
        """Name longer than 100 chars should raise error"""
        long_name = 'A' * 101
        with self.assertRaises(ValidationError) as cm:
            FieldValidator.validate_name(long_name, 'First Name')
        self.assertIn("exceed 100 characters", cm.exception.message)
    
    def test_name_with_numbers_raises_error(self):
        """Name with numbers should raise error"""
        with self.assertRaises(ValidationError):
            FieldValidator.validate_name('John123', 'First Name')
    
    def test_name_with_special_chars_raises_error(self):
        """Name with special characters should raise error"""
        with self.assertRaises(ValidationError):
            FieldValidator.validate_name('John@Doe', 'First Name')
    
    def test_name_whitespace_stripped(self):
        """Name whitespace should be stripped"""
        name = FieldValidator.validate_name('  John  ', 'First Name')
        self.assertEqual(name, 'John')


class FieldValidatorPhoneTests(TestCase):
    """Test phone validation"""
    
    def test_empty_phone_is_optional(self):
        """Empty phone should return empty string (optional)"""
        phone = FieldValidator.validate_phone('')
        self.assertEqual(phone, '')
    
    def test_valid_phone_format(self):
        """Valid phone should pass"""
        phone = FieldValidator.validate_phone('555-1234')
        self.assertEqual(phone, '555-1234')
    
    def test_phone_with_parentheses(self):
        """Phone with parentheses should pass"""
        phone = FieldValidator.validate_phone('(555) 123-4567')
        self.assertEqual(phone, '(555) 123-4567')
    
    def test_phone_too_long(self):
        """Phone longer than 15 chars should raise error"""
        long_phone = '1' * 16
        with self.assertRaises(ValidationError) as cm:
            FieldValidator.validate_phone(long_phone)
        self.assertIn("exceed 15 characters", cm.exception.message)
    
    def test_phone_with_invalid_chars(self):
        """Phone with invalid characters should raise error"""
        with self.assertRaises(ValidationError):
            FieldValidator.validate_phone('555-abc-1234')


class FieldValidatorTitleTests(TestCase):
    """Test story title validation"""
    
    def test_valid_title(self):
        """Valid title should pass"""
        title = FieldValidator.validate_title('My Amazing Story')
        self.assertEqual(title, 'My Amazing Story')
    
    def test_title_minimum_length(self):
        """Title with exactly 5 characters should pass"""
        title = FieldValidator.validate_title('Abcde')
        self.assertEqual(title, 'Abcde')
    
    def test_title_maximum_length(self):
        """Title with 500 characters should pass"""
        title_text = 'A' * 500
        title = FieldValidator.validate_title(title_text)
        self.assertEqual(title, title_text)
    
    def test_title_too_short(self):
        """Title with less than 5 chars should raise error"""
        with self.assertRaises(ValidationError) as cm:
            FieldValidator.validate_title('Test')
        self.assertIn("at least 5 characters", cm.exception.message)
    
    def test_title_too_long(self):
        """Title longer than 500 chars should raise error"""
        long_title = 'A' * 501
        with self.assertRaises(ValidationError) as cm:
            FieldValidator.validate_title(long_title)
        self.assertIn("exceed 500 characters", cm.exception.message)
    
    def test_empty_title_raises_error(self):
        """Empty title should raise error"""
        with self.assertRaises(ValidationError):
            FieldValidator.validate_title('')
    
    def test_title_starting_with_special_char(self):
        """Title starting with special char should raise error"""
        with self.assertRaises(ValidationError):
            FieldValidator.validate_title('!Invalid Title')
    
    def test_title_whitespace_stripped(self):
        """Title whitespace should be stripped"""
        title = FieldValidator.validate_title('  My Story  ')
        self.assertEqual(title, 'My Story')


class FieldValidatorStoryContentTests(TestCase):
    """Test story content validation"""
    
    def test_valid_story_content(self):
        """Valid story content should pass"""
        story = 'This is a story with at least 20 characters here.'
        content = FieldValidator.validate_story_content(story)
        self.assertEqual(content, story)
    
    def test_content_minimum_length(self):
        """Content with exactly 20 characters should pass"""
        content_text = 'A' * 20
        content = FieldValidator.validate_story_content(content_text)
        self.assertEqual(content, content_text)
    
    def test_content_maximum_length(self):
        """Content with 2000 characters should pass"""
        content_text = 'A' * 2000
        content = FieldValidator.validate_story_content(content_text)
        self.assertEqual(content, content_text)
    
    def test_content_too_short(self):
        """Content with less than 20 chars should raise error"""
        with self.assertRaises(ValidationError) as cm:
            FieldValidator.validate_story_content('Short')
        self.assertIn("at least 20 characters", cm.exception.message)
    
    def test_content_too_long(self):
        """Content longer than 2000 chars should raise error"""
        long_content = 'A' * 2001
        with self.assertRaises(ValidationError) as cm:
            FieldValidator.validate_story_content(long_content)
        self.assertIn("exceed 2000 characters", cm.exception.message)
    
    def test_empty_content_raises_error(self):
        """Empty content should raise error"""
        with self.assertRaises(ValidationError):
            FieldValidator.validate_story_content('')
    
    def test_content_whitespace_stripped(self):
        """Content whitespace should be stripped"""
        content = FieldValidator.validate_story_content(
            '  This is a story with at least 20 characters.  '
        )
        self.assertEqual(content, 'This is a story with at least 20 characters.')


class ValidateStorySubmissionTests(TestCase):
    """Test complete story submission validation"""
    
    def test_valid_submission(self):
        """Valid submission should return cleaned data"""
        data = {
            'email': 'john@gmail.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'phone': '555-1234',
            'title': 'My Story',
            'story': 'This is a story with at least 20 characters here.'
        }
        cleaned = validate_story_submission(data)
        
        self.assertEqual(cleaned['email'], 'john@gmail.com')
        self.assertEqual(cleaned['first_name'], 'John')
        self.assertEqual(cleaned['last_name'], 'Doe')
        self.assertEqual(cleaned['phone'], '555-1234')
        self.assertEqual(cleaned['title'], 'My Story')
    
    def test_submission_without_phone(self):
        """Submission without phone should work"""
        data = {
            'email': 'john@gmail.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'phone': '',
            'title': 'My Story',
            'story': 'This is a story with at least 20 characters here.'
        }
        cleaned = validate_story_submission(data)
        self.assertEqual(cleaned['phone'], '')
    
    def test_submission_email_lowercase(self):
        """Email should be converted to lowercase"""
        data = {
            'email': 'JOHN@GMAIL.COM',
            'first_name': 'John',
            'last_name': 'Doe',
            'title': 'My Story',
            'story': 'This is a story with at least 20 characters here.'
        }
        cleaned = validate_story_submission(data)
        self.assertEqual(cleaned['email'], 'john@gmail.com')
    
    def test_multiple_validation_errors(self):
        """Multiple field errors should raise ValidationErrorList"""
        data = {
            'email': 'invalid',
            'first_name': 'A',  # Too short
            'last_name': 'Doe',
            'title': 'Bad',  # Too short
            'story': 'Short'  # Too short
        }
        
        with self.assertRaises(ValidationErrorList) as cm:
            validate_story_submission(data)
        
        errors = cm.exception.field_errors
        self.assertIn('email', errors)
        self.assertIn('first_name', errors)
        self.assertIn('title', errors)
        self.assertIn('story', errors)
    
    def test_missing_required_field(self):
        """Missing required field should raise error"""
        data = {
            'email': 'john@gmail.com',
            'first_name': 'John',
            # Missing last_name
            'title': 'My Story',
            'story': 'This is a story with at least 20 characters here.'
        }
        
        with self.assertRaises(ValidationErrorList) as cm:
            validate_story_submission(data)
        
        errors = cm.exception.field_errors
        self.assertIn('last_name', errors)
    
    def test_all_fields_stripped_and_cleaned(self):
        """All string fields should be stripped of whitespace"""
        data = {
            'email': '  john@gmail.com  ',
            'first_name': '  John  ',
            'last_name': '  Doe  ',
            'phone': '  555-1234  ',
            'title': '  My Story  ',
            'story': '  This is a story with at least 20 characters.  '
        }
        
        cleaned = validate_story_submission(data)
        
        self.assertEqual(cleaned['email'], 'john@gmail.com')
        self.assertEqual(cleaned['first_name'], 'John')
        self.assertEqual(cleaned['last_name'], 'Doe')
        self.assertEqual(cleaned['phone'], '555-1234')
        self.assertEqual(cleaned['title'], 'My Story')
        self.assertIn('at least 20 characters', cleaned['story'])