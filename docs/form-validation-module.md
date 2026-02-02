# Form Validation Module Documentation

## Overview

The Form Validation Module provides real-time form validation with support for various validation rules. It integrates seamlessly with the design system's form field CSS classes for visual feedback.

**File Location:** `main/static/js/form-validation.js`

**Requirements:** 6.2, 6.3, 6.4, 6.5, 6.7

## Features

- ✅ Real-time validation on blur events
- ✅ Inline error messages
- ✅ Visual feedback with CSS classes (is-valid, is-invalid)
- ✅ Form submission prevention when validation fails
- ✅ Multiple validation rules support
- ✅ Custom validator functions
- ✅ Accessibility support (ARIA attributes)
- ✅ Automatic focus on first error field

## Installation

Include the script in your HTML template:

```html
<script src="{% static 'js/form-validation.js' %}"></script>
```

## Basic Usage

### 1. HTML Structure

Your form fields should follow this structure:

```html
<form id="myForm">
    <div class="form-field">
        <label class="form-field__label" for="email">Email Address</label>
        <input 
            type="email" 
            id="email" 
            name="email"
            class="form-field__input" 
            placeholder="you@example.com"
            aria-describedby="email-error"
        >
        <span class="form-field__error" id="email-error" role="alert"></span>
        <span class="form-field__helper">We'll never share your email</span>
    </div>
    
    <button type="submit" class="btn btn--primary">Submit</button>
</form>
```

### 2. JavaScript Initialization

```javascript
// Define validation rules
const validationRules = {
    email: {
        required: true,
        pattern: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
        message: 'Please enter a valid email address'
    },
    password: {
        required: true,
        minLength: 8,
        message: 'Password must be at least 8 characters'
    }
};

// Create validator instance
const form = document.getElementById('myForm');
const validator = new FormValidator(form, validationRules);

// Initialize validation
validator.init();
```

## Validation Rules

### Required Field

```javascript
{
    required: true,
    message: 'This field is required'
}
```

### Pattern Matching (Regex)

```javascript
{
    pattern: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
    message: 'Please enter a valid email address'
}
```

### Minimum Length

```javascript
{
    minLength: 8,
    message: 'Minimum 8 characters required'
}
```

### Maximum Length

```javascript
{
    maxLength: 50,
    message: 'Maximum 50 characters allowed'
}
```

### Minimum Value (Numbers)

```javascript
{
    min: 1,
    message: 'Minimum value is 1'
}
```

### Maximum Value (Numbers)

```javascript
{
    max: 99,
    message: 'Maximum value is 99'
}
```

### Custom Validator Function

```javascript
{
    validator: (value) => {
        const age = parseInt(value);
        if (age >= 18 && age <= 100) {
            return true;
        }
        return 'Age must be between 18 and 100';
    }
}
```

### Optional Fields

```javascript
{
    required: false,
    pattern: /^\d{10}$/,
    message: 'Please enter a valid phone number'
}
```

## Complete Examples

### Login Form

```javascript
const loginRules = {
    email: {
        required: true,
        pattern: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
        message: 'Please enter a valid email address'
    },
    password: {
        required: true,
        minLength: 8,
        message: 'Password must be at least 8 characters'
    }
};

const loginForm = document.getElementById('loginForm');
const loginValidator = new FormValidator(loginForm, loginRules);
loginValidator.init();
```

### Order Form

```javascript
const orderRules = {
    dishQuantity: {
        required: true,
        min: 1,
        max: 99,
        message: 'Quantity must be between 1 and 99'
    },
    specialInstructions: {
        required: false,
        maxLength: 200,
        message: 'Maximum 200 characters allowed'
    }
};

const orderForm = document.getElementById('orderForm');
const orderValidator = new FormValidator(orderForm, orderRules);
orderValidator.init();
```

### Profile Form with Custom Validation

```javascript
const profileRules = {
    username: {
        required: true,
        minLength: 3,
        maxLength: 20,
        pattern: /^[a-zA-Z0-9_]+$/,
        message: 'Username must be 3-20 characters (letters, numbers, underscore only)'
    },
    age: {
        required: true,
        validator: (value) => {
            const age = parseInt(value);
            if (isNaN(age)) return 'Please enter a valid number';
            if (age < 18) return 'You must be at least 18 years old';
            if (age > 120) return 'Please enter a valid age';
            return true;
        }
    },
    phone: {
        required: false,
        pattern: /^\d{10,11}$/,
        message: 'Please enter a valid phone number (10-11 digits)'
    }
};

const profileForm = document.getElementById('profileForm');
const profileValidator = new FormValidator(profileForm, profileRules);
profileValidator.init();
```

## Advanced Usage

### Custom Submit Handler

Instead of the default form submission, you can provide a custom handler:

```javascript
const validator = new FormValidator(form, rules);

validator.setSubmitHandler((formData) => {
    // Custom submission logic
    console.log('Form data:', Object.fromEntries(formData));
    
    // Make AJAX request
    fetch('/api/submit/', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        console.log('Success:', data);
        // Show success message
    })
    .catch(error => {
        console.error('Error:', error);
        // Show error message
    });
});

validator.init();
```

### Manual Validation

You can manually validate fields or the entire form:

```javascript
// Validate a single field
const result = validator.validateField('email', 'test@example.com');
if (!result.valid) {
    console.log('Error:', result.message);
}

// Validate entire form
if (validator.validateForm()) {
    console.log('Form is valid');
} else {
    console.log('Form has errors:', validator.errors);
}

// Show/clear errors manually
validator.showError('email', 'This email is already taken');
validator.clearError('email');
validator.clearAllErrors();
```

## API Reference

### Constructor

```javascript
new FormValidator(formElement, rules)
```

**Parameters:**
- `formElement` (HTMLFormElement): The form element to validate
- `rules` (Object): Validation rules for form fields

### Methods

#### `validateField(fieldName, value)`

Validates a single field.

**Parameters:**
- `fieldName` (string): The name of the field
- `value` (string): The value to validate

**Returns:** `{ valid: boolean, message?: string }`

#### `validateForm()`

Validates the entire form.

**Returns:** `boolean` - True if form is valid

#### `showError(fieldName, message)`

Displays an error message for a field.

**Parameters:**
- `fieldName` (string): The name of the field
- `message` (string): The error message

#### `clearError(fieldName)`

Clears the error for a field.

**Parameters:**
- `fieldName` (string): The name of the field

#### `clearAllErrors()`

Clears all errors in the form.

#### `init()`

Initializes real-time validation with event listeners.

#### `setSubmitHandler(handler)`

Sets a custom submit handler.

**Parameters:**
- `handler` (Function): Function to call on successful validation

## CSS Integration

The validator automatically adds/removes these CSS classes:

- `.is-invalid` - Added to invalid fields
- `.is-valid` - Added to valid fields
- `.form-field__error` - Error message container (shown when field is invalid)

Example CSS:

```css
.form-field__input.is-invalid {
    border-color: var(--color-error);
}

.form-field__input.is-valid {
    border-color: var(--color-success);
}

.form-field__error {
    display: none;
    color: var(--color-error);
}

.form-field__input.is-invalid ~ .form-field__error {
    display: block;
}
```

## Accessibility

The validator includes accessibility features:

- Sets `aria-invalid="true"` on invalid fields
- Sets `aria-invalid="false"` on valid fields
- Error messages have `role="alert"` for screen reader announcements
- Automatically focuses on the first error field when form submission fails

## Browser Support

- Modern browsers (Chrome, Firefox, Safari, Edge)
- IE11+ (with polyfills for FormData)

## Testing

Test page available at: `/test/form-validation/`

Run unit tests:
```bash
python test_form_validation.py
```

## Common Patterns

### Password Confirmation

```javascript
const rules = {
    password: {
        required: true,
        minLength: 8,
        message: 'Password must be at least 8 characters'
    },
    confirmPassword: {
        required: true,
        validator: (value) => {
            const password = document.getElementById('password').value;
            return value === password ? true : 'Passwords do not match';
        }
    }
};
```

### Conditional Validation

```javascript
const rules = {
    shippingAddress: {
        validator: (value) => {
            const needsShipping = document.getElementById('needsShipping').checked;
            if (needsShipping && !value) {
                return 'Shipping address is required';
            }
            return true;
        }
    }
};
```

### Multiple Patterns

```javascript
const rules = {
    username: {
        required: true,
        minLength: 3,
        pattern: /^[a-zA-Z0-9_]+$/,
        validator: (value) => {
            // Additional custom validation
            if (value.toLowerCase() === 'admin') {
                return 'Username "admin" is reserved';
            }
            return true;
        }
    }
};
```

## Troubleshooting

### Validation not working

1. Ensure the form has the correct structure with `.form-field__error` elements
2. Check that field names match the validation rules
3. Verify that `validator.init()` is called after DOM is loaded

### Error messages not showing

1. Check that CSS classes are properly defined
2. Ensure `.form-field__error` element exists for each field
3. Verify that the error element has the correct `id` matching `aria-describedby`

### Form submitting despite errors

1. Ensure `validator.init()` is called to attach the submit event listener
2. Check browser console for JavaScript errors
3. Verify that the form element is correctly passed to the constructor

## Related Documentation

- [Design System](design-system.md)
- [Form Field Component](components.md#form-field)
- [Accessibility Guidelines](accessibility.md)

## Requirements Mapping

- **Requirement 6.2**: Inline error messages for invalid data
- **Requirement 6.3**: Real-time validation on blur event
- **Requirement 6.4**: Form submission prevention with errors
- **Requirement 6.5**: Success feedback for valid fields
- **Requirement 6.7**: Submit button disabled during processing
