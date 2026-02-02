# Toast Notification Module

A lightweight, accessible toast notification system for displaying user feedback messages.

## Features

- ✅ Multiple notification types (success, error, warning, info)
- ✅ Auto-dismiss with configurable duration
- ✅ Manual dismiss via close button
- ✅ Screen reader accessibility (ARIA live regions)
- ✅ Keyboard navigation support
- ✅ Smooth animations (respects prefers-reduced-motion)
- ✅ Maximum toast limit (prevents overflow)
- ✅ XSS protection (HTML escaping)
- ✅ Responsive design (mobile-friendly)
- ✅ No external dependencies

## Requirements

This module satisfies the following requirements:
- **15.3**: Display success/error messages for user actions
- **15.4**: Auto-dismiss notifications after configurable duration
- **12.5**: Screen reader announcements for dynamic content

## Installation

### 1. Include CSS

Add the following CSS files to your HTML:

```html
<link rel="stylesheet" href="{% static 'css/design-system.css' %}">
<link rel="stylesheet" href="{% static 'css/base-components.css' %}">
<link rel="stylesheet" href="{% static 'css/components.css' %}">
```

### 2. Include JavaScript

Add the toast.js script before the closing `</body>` tag:

```html
<script src="{% static 'js/toast.js' %}"></script>
```

## Usage

### Basic Usage

The toast module creates a global `window.toast` instance that you can use anywhere in your application:

```javascript
// Show a success toast (default 5 second duration)
window.toast.show('Order submitted successfully!', 'success');

// Show an error toast
window.toast.show('Failed to submit order', 'error');

// Show a warning toast
window.toast.show('Your session will expire soon', 'warning');

// Show an info toast
window.toast.show('New dishes available', 'info');
```

### Custom Duration

Specify a custom duration in milliseconds (third parameter):

```javascript
// Show for 2 seconds
window.toast.show('Quick message', 'success', 2000);

// Show for 10 seconds
window.toast.show('Important message', 'warning', 10000);

// No auto-dismiss (must be manually closed)
window.toast.show('Persistent message', 'info', 0);
```

### Dismiss Toasts

```javascript
// Dismiss a specific toast
const toast = window.toast.show('Message', 'info');
window.toast.dismiss(toast);

// Dismiss all toasts
window.toast.dismissAll();
```

### Configuration Options

You can configure the ToastManager when creating a custom instance:

```javascript
const customToast = new ToastManager({
  position: 'top-right',      // Position: top-right, top-left, top-center, bottom-right, bottom-left, bottom-center
  defaultDuration: 5000,      // Default duration in milliseconds
  maxToasts: 5                // Maximum number of toasts to display at once
});

customToast.show('Custom toast', 'success');
```

## API Reference

### ToastManager Class

#### Constructor

```javascript
new ToastManager(options)
```

**Parameters:**
- `options` (Object, optional)
  - `position` (String): Toast container position. Default: `'top-right'`
  - `defaultDuration` (Number): Default auto-dismiss duration in ms. Default: `5000`
  - `maxToasts` (Number): Maximum number of toasts to display. Default: `5`

#### Methods

##### show(message, type, duration)

Display a toast notification.

**Parameters:**
- `message` (String, required): The message to display
- `type` (String, optional): Toast type - `'success'`, `'error'`, `'warning'`, or `'info'`. Default: `'success'`
- `duration` (Number, optional): Duration in milliseconds. Use `0` for no auto-dismiss. Default: uses `defaultDuration`

**Returns:** HTMLElement - The created toast element

**Example:**
```javascript
window.toast.show('Order submitted!', 'success', 3000);
```

##### dismiss(toast)

Dismiss a specific toast notification.

**Parameters:**
- `toast` (HTMLElement, required): The toast element to dismiss

**Example:**
```javascript
const toast = window.toast.show('Message', 'info');
window.toast.dismiss(toast);
```

##### dismissAll()

Dismiss all active toast notifications.

**Example:**
```javascript
window.toast.dismissAll();
```

## Integration Examples

### Django Form Submission

```javascript
// In your form submission handler
document.querySelector('#order-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  
  const formData = new FormData(e.target);
  
  try {
    const response = await fetch('/api/submit_order/', {
      method: 'POST',
      body: formData,
      headers: {
        'X-CSRFToken': getCookie('csrftoken')
      }
    });
    
    const data = await response.json();
    
    if (data.success) {
      window.toast.show('Order submitted successfully!', 'success');
      // Redirect or update UI
    } else {
      window.toast.show(data.message || 'Failed to submit order', 'error');
    }
  } catch (error) {
    window.toast.show('Network error. Please try again.', 'error');
  }
});
```

### AJAX Request

```javascript
// Show loading toast
const loadingToast = window.toast.show('Loading...', 'info', 0);

fetch('/api/data/')
  .then(response => response.json())
  .then(data => {
    // Dismiss loading toast
    window.toast.dismiss(loadingToast);
    
    // Show success toast
    window.toast.show('Data loaded successfully!', 'success');
  })
  .catch(error => {
    // Dismiss loading toast
    window.toast.dismiss(loadingToast);
    
    // Show error toast
    window.toast.show('Failed to load data', 'error');
  });
```

### Validation Feedback

```javascript
// Form validation
function validateForm() {
  const email = document.querySelector('#email').value;
  
  if (!email) {
    window.toast.show('Email is required', 'error', 3000);
    return false;
  }
  
  if (!isValidEmail(email)) {
    window.toast.show('Please enter a valid email address', 'error', 3000);
    return false;
  }
  
  window.toast.show('Form is valid!', 'success', 2000);
  return true;
}
```

## Accessibility

The toast notification module is designed with accessibility in mind:

### Screen Reader Support

- Toasts use `role="alert"` and `aria-live="assertive"` for immediate announcements
- A separate screen reader announcement is created for each toast
- The `.sr-only` class ensures announcements are read but not visible

### Keyboard Navigation

- Close buttons are keyboard accessible (Tab key)
- Enter or Space key can dismiss toasts
- Visible focus indicators on close buttons

### Reduced Motion

- Respects `prefers-reduced-motion` media query
- Animations are disabled for users who prefer reduced motion
- Toasts still appear but without sliding animations

## Styling

### CSS Variables

The toast component uses CSS custom properties from the design system:

```css
/* Colors */
--color-success: #10b981;
--color-error: #ef4444;
--color-warning: #f59e0b;
--color-info: #3b82f6;

/* Spacing */
--spacing-3: 0.75rem;
--spacing-4: 1rem;

/* Shadows */
--shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1);

/* Border Radius */
--radius-lg: 1rem;

/* Z-index */
--z-index-toast: 2000;
```

### Custom Styling

You can customize toast appearance by overriding CSS classes:

```css
/* Custom toast background */
.toast {
  background-color: #ffffff;
  border: 2px solid #e5e7eb;
}

/* Custom success color */
.toast--success {
  border-left-color: #059669;
}

/* Custom icon size */
.toast__icon {
  width: 32px;
  height: 32px;
  font-size: 1rem;
}
```

## Browser Support

- Chrome/Edge: ✅ Full support
- Firefox: ✅ Full support
- Safari: ✅ Full support
- Mobile browsers: ✅ Full support
- IE11: ⚠️ Requires polyfills for modern JavaScript features

## Demo

Open `toast-demo.html` in your browser to see the toast notification system in action.

## Testing

### Manual Testing Checklist

- [ ] Success toast displays with green color
- [ ] Error toast displays with red color
- [ ] Warning toast displays with yellow/orange color
- [ ] Info toast displays with blue color
- [ ] Toasts auto-dismiss after specified duration
- [ ] Close button dismisses toast immediately
- [ ] Multiple toasts stack vertically
- [ ] Maximum toast limit is enforced
- [ ] Toasts are responsive on mobile devices
- [ ] Screen reader announces toast messages
- [ ] Keyboard navigation works (Tab, Enter, Space)
- [ ] Focus indicators are visible
- [ ] Animations respect prefers-reduced-motion

### Automated Testing

```javascript
// Example test with Jest or similar framework
describe('ToastManager', () => {
  let toast;
  
  beforeEach(() => {
    toast = new ToastManager();
  });
  
  test('shows success toast', () => {
    const element = toast.show('Success!', 'success');
    expect(element.classList.contains('toast--success')).toBe(true);
  });
  
  test('auto-dismisses after duration', (done) => {
    const element = toast.show('Test', 'info', 1000);
    
    setTimeout(() => {
      expect(document.body.contains(element)).toBe(false);
      done();
    }, 1500);
  });
  
  test('escapes HTML in messages', () => {
    const element = toast.show('<script>alert("xss")</script>', 'info');
    expect(element.innerHTML).not.toContain('<script>');
  });
});
```

## Troubleshooting

### Toasts not appearing

1. Ensure CSS files are loaded correctly
2. Check browser console for JavaScript errors
3. Verify `window.toast` is defined
4. Check z-index conflicts with other elements

### Toasts not dismissing

1. Check if duration is set to 0 (persistent)
2. Verify JavaScript is not throwing errors
3. Check if `setTimeout` is working correctly

### Styling issues

1. Ensure design-system.css is loaded first
2. Check for CSS specificity conflicts
3. Verify CSS custom properties are defined
4. Check browser DevTools for applied styles

## License

This module is part of the DashBoard restaurant ordering system.

## Support

For issues or questions, please refer to the project documentation or contact the development team.
