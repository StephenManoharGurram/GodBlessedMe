"""
stories/validator.py

Input validation for story submissions.
Validates: email, names, phone, title, story content.
Returns validation errors in structured format.
"""

import re


class ValidationError(Exception):
    """Custom validation error for story submission"""
    
    def __init__(self, message, field=None):
        """
        Args:
            message (str): Error message
            field (str): Field name where error occurred
        """
        self.message = message
        self.field = field
        super().__init__(self.message)


class FieldValidator:
    """Centralized field validation"""
    
    @staticmethod
    def validate_email(email):
        """
        Validate email format.
        
        Args:
            email (str): Email address to validate
            
        Returns:
            str: Cleaned email (lowercase)
            
        Raises:
            ValidationError: If email is invalid
        """
        if not email:
            raise ValidationError("Email is required")
        
        email = email.strip().lower()
        
        # Basic email regex
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, email):
            raise ValidationError("Invalid email format")
        
        if len(email) > 254:
            raise ValidationError("Email is too long (max 254 characters)")
        
        return email
    
    @staticmethod
    def validate_name(name, field_name="Name"):
        """
        Validate first/last name.
        
        Args:
            name (str): Name to validate
            field_name (str): "First Name" or "Last Name" for error messages
            
        Returns:
            str: Cleaned name (stripped whitespace)
            
        Raises:
            ValidationError: If name is invalid
        """
        if not name:
            raise ValidationError(f"{field_name} is required")
        
        name = name.strip()
        
        # Check length
        if len(name) < 2:
            raise ValidationError(f"{field_name} must be at least 2 characters")
        
        if len(name) > 100:
            raise ValidationError(f"{field_name} must not exceed 100 characters")
        
        # Check for valid characters (letters, hyphens, spaces, apostrophes)
        # Allow: a-z, A-Z, hyphens, spaces, apostrophes
        name_regex = r"^[a-zA-Z\s\-']+$"
        if not re.match(name_regex, name):
            raise ValidationError(
                f"{field_name} can only contain letters, hyphens, spaces, and apostrophes"
            )
        
        return name
    
    @staticmethod
    def validate_phone(phone):
        """
        Validate phone number (optional field).
        
        Args:
            phone (str): Phone number to validate
            
        Returns:
            str: Cleaned phone number
            
        Raises:
            ValidationError: If phone is invalid format
        """
        if not phone or phone.strip() == "":
            return ""  # Phone is optional
        
        phone = phone.strip()
        
        # Allow up to 15 characters (international format can be longer)
        if len(phone) > 15:
            raise ValidationError("Phone number must not exceed 15 characters")
        
        # Allow digits, spaces, hyphens, parentheses, plus sign
        phone_regex = r"^[\d\s\-()+ ]+$"
        if not re.match(phone_regex, phone):
            raise ValidationError("Phone number contains invalid characters")
        
        return phone
    
    @staticmethod
    def validate_title(title):
        """
        Validate story title.
        
        Args:
            title (str): Story title to validate
            
        Returns:
            str: Cleaned title
            
        Raises:
            ValidationError: If title is invalid
        """
        if not title:
            raise ValidationError("Story title is required")
        
        title = title.strip()
        
        # Check length
        if len(title) < 5:
            raise ValidationError("Story title must be at least 5 characters")
        
        if len(title) > 500:
            raise ValidationError("Story title must not exceed 500 characters")
        
        # Check for basic validity (no leading/trailing special chars)
        if title[0] in ['!', '@', '#', '$', '%']:
            raise ValidationError("Story title cannot start with special characters")
        
        return title
    
    @staticmethod
    def validate_story_content(content):
        """
        Validate story body content.
        
        Args:
            content (str): Story content to validate
            
        Returns:
            str: Cleaned content
            
        Raises:
            ValidationError: If content is invalid
        """
        if not content:
            raise ValidationError("Story content is required")
        
        content = content.strip()
        
        # Check length
        if len(content) < 20:
            raise ValidationError("Story must be at least 20 characters")
        
        if len(content) > 2000:
            raise ValidationError("Story must not exceed 2000 characters")
        
        return content


class ValidationErrorList(Exception):
    """Exception for multiple field validation errors"""
    
    def __init__(self, field_errors):
        """
        Args:
            field_errors (dict): Dictionary of field names to error lists
        """
        self.field_errors = field_errors
        self.message = f"Validation failed for {len(field_errors)} field(s)"
        super().__init__(self.message)


def validate_story_submission(data):
    """
    Validate entire story submission payload.
    
    Args:
        data (dict): Submission data with keys:
            - email
            - first_name
            - last_name
            - phone (optional)
            - title
            - story
    
    Returns:
        dict: Cleaned and validated data
        
    Raises:
        ValidationErrorList: If validation fails with field errors
        
    Example:
        try:
            cleaned_data = validate_story_submission(payload)
        except ValidationErrorList as e:
            # Handle field_errors
            print(e.field_errors)
    """
    errors = {}
    cleaned_data = {}
    
    # Validate email
    try:
        cleaned_data['email'] = FieldValidator.validate_email(data.get('email'))
    except ValidationError as e:
        errors['email'] = [e.message]
    
    # Validate first name
    try:
        cleaned_data['first_name'] = FieldValidator.validate_name(
            data.get('first_name'), 
            "First Name"
        )
    except ValidationError as e:
        errors['first_name'] = [e.message]
    
    # Validate last name
    try:
        cleaned_data['last_name'] = FieldValidator.validate_name(
            data.get('last_name'), 
            "Last Name"
        )
    except ValidationError as e:
        errors['last_name'] = [e.message]
    
    # Validate phone (optional)
    try:
        cleaned_data['phone'] = FieldValidator.validate_phone(
            data.get('phone', '')
        )
    except ValidationError as e:
        errors['phone'] = [e.message]
    
    # Validate title
    try:
        cleaned_data['title'] = FieldValidator.validate_title(data.get('title'))
    except ValidationError as e:
        errors['title'] = [e.message]
    
    # Validate story content
    try:
        cleaned_data['story'] = FieldValidator.validate_story_content(
            data.get('story')
        )
    except ValidationError as e:
        errors['story'] = [e.message]
    
    # If there are errors, raise them
    if errors:
        raise ValidationErrorList(errors)
    
    return cleaned_data