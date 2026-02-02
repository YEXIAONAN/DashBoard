# Form Field Component Documentation

## Overview

The Form Field Component is a comprehensive, accessible form input system that provides consistent styling and validation states across all form inputs in the DashBoard application.

## Features

- ✅ **Multiple Input Types**: text, email, password, number, tel, url, date, time, textarea, select
- ✅ **Validation States**: Valid (green), Invalid (red), with visual indicators
- ✅ **Accessibility**: Proper label association, ARIA attributes, keyboard navigation
- ✅ **Responsive Design**: Mobile-friendly with adaptive layouts
- ✅ **Error Messages**: Inline error display with icons
- ✅ **Helper Text**: Contextual guidance for users
- ✅ **Focus States**: Clear visual feedback (Requirement 6.1)
- ✅ **Disabled States**: Proper styling for disabled inputs
- ✅ **Icons**: Built-in validation icons and search icon

## Requirements Satisfied

- **Requirement 6.1**: Focus states with visual indicators (border color change and shadow)
- **Requirement 6.2**: Inline error messages with validation styling
- **Requirement 12.4**: Proper label association for accessibility

## Basic Usage

### Standard Text Input

```html
<div class="form-field">
  <label class="form-field__label" for="username">Username</label>
  <input 
    type="text" 
    id="username" 
    name="username"
    class="form-field__input" 
    placeholder="Enter your username"
  >
  <span class="form-field__helper">Choose a unique username</span>
</div>
```

### Required Field

```html
<div class="form-field">
  <label class="form-field__label form-field__label--required" for="email">Email Address</label>
  <input 
    type="email" 
    id="email" 
    name="email"
    class="form-field__input" 
    placeholder="you@example.com"
    required
    aria-describedby="email-error email-helper"
  >
  <span class="form-field__error" id="email-error" role="alert"></span>
  <span class="form-field__helper" id="email-helper">We'll never share your email</span>
</div>
```

### Optional Field

```html
<div class="form-field">
  <label class="form-field__label form-field__label--optional" for="phone">Phone Number</label>
  <input 
    type="tel" 
    id="phone" 
    name="phone"
    class="form-field__input" 
    placeholder="(555) 123-4567"
  >
</div>
```

## Validation States

### Valid State

Add the `is-valid` class to show success styling:

```html
<input 
  type="email" 
  class="form-field__input is-valid" 
  value="user@example.com"
>
```

### Invalid State

Add the `is-invalid` class to show error styling and display error message:

```html
<input 
  type="email" 
  class="form-field__input is-invalid" 
  value="invalid-email"
  aria-describedby="email-error"
>
<span class="form-field__error" id="email-error" role="alert">
  Please enter a valid email address
</span>
```

## Input Types

### Textarea

```html
<div class="form-field">
  <label class="form-field__label" for="description">Description</label>
  <textarea 
    id="description" 
    name="description"
    class="form-field__textarea" 
    placeholder="Enter a description"
  ></textarea>
  <span class="form-field__helper">Maximum 500 characters</span>
</div>
```

### Select Dropdown

```html
<div class="form-field">
  <label class="form-field__label" for="category">Category</label>
  <select id="category" name="category" class="form-field__select">
    <option value="">Select a category</option>
    <option value="meat">Meat</option>
    <option value="vegetables">Vegetables</option>
    <option value="staples">Staples</option>
  </select>
</div>
```

### Number Input

```html
<div class="form-field">
  <label class="form-field__label" for="quantity">Quantity</label>
  <input 
    type="number" 
    id="quantity" 
    name="quantity"
    class="form-field__input" 
    min="1"
    max="99"
    value="1"
  >
  <span class="form-field__helper">Enter quantity (1-99)</span>
</div>
```

### Search Input

```html
<div class="form-field">
  <label class="form-field__label" for="search">Search</label>
  <input 
    type="search" 
    id="search" 
    name="search"
    class="form-field__input" 
    placeholder="Search dishes..."
  >
</div>
```

### Checkbox

```html
<div class="form-field form-field--checkbox">
  <input 
    type="checkbox" 
    id="terms" 
    name="terms"
    class="form-field__checkbox"
  >
  <label class="form-field__label" for="terms">
    I agree to the terms and conditions
  </label>
</div>
```

### Radio Buttons

```html
<div class="form-field form-field--radio">
  <input 
    type="radio" 
    id="gender-male" 
    name="gender"
    class="form-field__radio"
    value="male"
  >
  <label class="form-field__label" for="gender-male">Male</label>
</div>
```

## Variants

### Compact Form Field

Reduced spacing for dense layouts:

```html
<div class="form-field form-field--compact">
  <!-- form field content -->
</div>
```

### Inline Form Field

Label and input side by side:

```html
<div class="form-field form-field--inline">
  <label class="form-field__label" for="age">Age</label>
  <input type="number" id="age" class="form-field__input">
</div>
```

### Small Input

```html
<input type="text" class="form-field__input form-field__input--sm">
```

### Large Input

```html
<input type="text" class="form-field__input form-field__input--lg">
```

## Form Layouts

### Basic Form Container

```html
<form class="form">
  <div class="form-field">
    <!-- field 1 -->
  </div>
  <div class="form-field">
    <!-- field 2 -->
  </div>
  
  <div class="form-actions">
    <button type="button" class="btn btn--secondary">Cancel</button>
    <button type="submit" class="btn btn--primary">Submit</button>
  </div>
</form>
```

### Form Section

Group related fields with a title:

```html
<div class="form-section">
  <h3 class="form-section__title">Personal Information</h3>
  <p class="form-section__description">Please provide your personal details</p>
  
  <div class="form-field">
    <!-- fields -->
  </div>
</div>
```

### Form Field Group

Multiple inputs in a row:

```html
<div class="form-field-group">
  <div class="form-field">
    <label class="form-field__label" for="first-name">First Name</label>
    <input type="text" id="first-name" class="form-field__input">
  </div>
  
  <div class="form-field">
    <label class="form-field__label" for="last-name">Last Name</label>
    <input type="text" id="last-name" class="form-field__input">
  </div>
</div>
```

## JavaScript Integration

### Real-time Validation Example

```javascript
document.querySelectorAll('.form-field__input').forEach(input => {
  input.addEventListener('blur', function() {
    if (this.value && this.checkValidity()) {
      this.classList.remove('is-invalid');
      this.classList.add('is-valid');
    } else if (this.value && !this.checkValidity()) {
      this.classList.remove('is-valid');
      this.classList.add('is-invalid');
      
      // Show error message
      const errorElement = this.parentElement.querySelector('.form-field__error');
      if (errorElement) {
        errorElement.textContent = this.validationMessage;
      }
    }
  });
});
```

### Clear Validation on Input

```javascript
input.addEventListener('input', function() {
  if (this.classList.contains('is-invalid') || this.classList.contains('is-valid')) {
    if (this.value && this.checkValidity()) {
      this.classList.remove('is-invalid');
      this.classList.add('is-valid');
    }
  }
});
```

## Accessibility Features

1. **Label Association**: All inputs have properly associated labels using `for` and `id` attributes
2. **ARIA Attributes**: Error messages use `role="alert"` and inputs reference them with `aria-describedby`
3. **Focus Indicators**: Clear visual focus states with outline and shadow
4. **Keyboard Navigation**: All inputs are keyboard accessible
5. **Screen Reader Support**: Helper text and error messages are announced to screen readers
6. **Required Field Indicators**: Visual asterisk (*) for required fields

## Browser Support

- Chrome (latest 2 versions)
- Firefox (latest 2 versions)
- Safari (latest 2 versions)
- Edge (latest 2 versions)

## Responsive Behavior

- **Mobile (< 768px)**: 
  - Inline forms stack vertically
  - Form field groups stack vertically
  - Reduced padding for inputs
  - Form actions stack vertically

- **Tablet (768px - 1024px)**: 
  - Standard layout with optimized spacing

- **Desktop (> 1024px)**: 
  - Full layout with maximum spacing

## Testing

To test the form field component, visit:
```
http://localhost:8000/test/form-fields/
```

This test page demonstrates all form field variants, validation states, and input types.

## CSS Classes Reference

### Container Classes
- `.form-field` - Main container for a form field
- `.form-field--compact` - Reduced spacing variant
- `.form-field--inline` - Horizontal layout variant
- `.form-field--checkbox` - Checkbox layout
- `.form-field--radio` - Radio button layout

### Label Classes
- `.form-field__label` - Standard label
- `.form-field__label--required` - Shows asterisk for required fields
- `.form-field__label--optional` - Shows "(optional)" text
- `.form-field__label--disabled` - Disabled label styling

### Input Classes
- `.form-field__input` - Standard text input
- `.form-field__textarea` - Textarea
- `.form-field__select` - Select dropdown
- `.form-field__checkbox` - Checkbox input
- `.form-field__radio` - Radio input
- `.form-field__input--sm` - Small size variant
- `.form-field__input--lg` - Large size variant

### State Classes
- `.is-valid` - Valid state (green border, checkmark icon)
- `.is-invalid` - Invalid state (red border, X icon)

### Message Classes
- `.form-field__error` - Error message (shown when input is invalid)
- `.form-field__helper` - Helper text (hidden when error is shown)

### Layout Classes
- `.form` - Form container
- `.form--wide` - Full width form
- `.form--narrow` - Narrow form (400px max)
- `.form-section` - Grouped form section with title
- `.form-field-group` - Horizontal group of fields
- `.form-actions` - Form button container

## Best Practices

1. **Always associate labels with inputs** using `for` and `id` attributes
2. **Use appropriate input types** (email, tel, number, etc.) for better mobile keyboards
3. **Provide helper text** for complex or important fields
4. **Show validation on blur** rather than on every keystroke
5. **Use clear, actionable error messages** that tell users how to fix the problem
6. **Mark required fields** with the `form-field__label--required` class
7. **Group related fields** using `form-section` or `form-field-group`
8. **Test with keyboard navigation** to ensure accessibility

## Examples in Existing Pages

The form field component should be used in:

- **login.html** - Login form (email, password)
- **profile.html** - Profile editing form (name, email, phone, health data)
- **orders.html** - Quantity inputs for dish ordering
- **ai_health_advisor.html** - Message input field

## Migration Guide

To update existing forms to use the new component:

1. Replace custom form markup with `.form-field` structure
2. Add proper label associations
3. Include error and helper text elements
4. Add validation state classes (`.is-valid`, `.is-invalid`)
5. Update JavaScript to toggle validation classes
6. Test keyboard navigation and screen reader compatibility

## Support

For questions or issues with the form field component, refer to:
- Design document: `.kiro/specs/frontend-ui-optimization/design.md`
- Requirements: `.kiro/specs/frontend-ui-optimization/requirements.md`
- Component CSS: `main/static/css/components.css`
