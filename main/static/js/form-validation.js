/**
 * Form Validation Module
 * 
 * Provides real-time form validation with support for various validation rules.
 * Integrates with form field CSS classes (is-valid, is-invalid) for visual feedback.
 * 
 * Requirements: 6.2, 6.3, 6.4, 6.5, 6.7
 */

class FormValidator {
  /**
   * Create a new FormValidator instance
   * @param {HTMLFormElement} formElement - The form element to validate
   * @param {Object} rules - Validation rules for form fields
   * @example
   * const validator = new FormValidator(document.querySelector('#myForm'), {
   *   email: {
   *     required: true,
   *     pattern: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
   *     message: 'Please enter a valid email address'
   *   },
   *   password: {
   *     required: true,
   *     minLength: 8,
   *     message: 'Password must be at least 8 characters'
   *   }
   * });
   */
  constructor(formElement, rules) {
    this.form = formElement;
    this.rules = rules;
    this.errors = {};
  }
  
  /**
   * Validate a single field
   * @param {string} fieldName - The name of the field to validate
   * @param {string} value - The value to validate
   * @returns {Object} Validation result with valid flag and optional message
   */
  validateField(fieldName, value) {
    const rule = this.rules[fieldName];
    if (!rule) return { valid: true };
    
    // Normalize value by trimming whitespace
    const trimmedValue = value ? value.trim() : '';
    
    // Check required
    if (rule.required && trimmedValue === '') {
      return { 
        valid: false, 
        message: rule.message || `${this.formatFieldName(fieldName)} is required` 
      };
    }
    
    // If field is not required and empty (after trim), it's valid
    if (!rule.required && trimmedValue === '') {
      return { valid: true };
    }
    
    // For non-empty values (required or optional), apply all other validations
    // Check pattern
    if (rule.pattern && !rule.pattern.test(trimmedValue)) {
      return { 
        valid: false, 
        message: rule.message || `${this.formatFieldName(fieldName)} format is invalid` 
      };
    }
    
    // Check minLength
    if (rule.minLength && trimmedValue.length < rule.minLength) {
      return { 
        valid: false, 
        message: rule.message || `Minimum ${rule.minLength} characters required` 
      };
    }
    
    // Check maxLength
    if (rule.maxLength && trimmedValue.length > rule.maxLength) {
      return { 
        valid: false, 
        message: rule.message || `Maximum ${rule.maxLength} characters allowed` 
      };
    }
    
    // Check min value (for numbers)
    if (rule.min !== undefined) {
      const numValue = parseFloat(trimmedValue);
      if (isNaN(numValue) || numValue < rule.min) {
        return { 
          valid: false, 
          message: rule.message || `Minimum value is ${rule.min}` 
        };
      }
    }
    
    // Check max value (for numbers)
    if (rule.max !== undefined) {
      const numValue = parseFloat(trimmedValue);
      if (isNaN(numValue) || numValue > rule.max) {
        return { 
          valid: false, 
          message: rule.message || `Maximum value is ${rule.max}` 
        };
      }
    }
    
    // Check custom validator function
    if (rule.validator && typeof rule.validator === 'function') {
      const customResult = rule.validator(trimmedValue);
      if (customResult !== true) {
        return {
          valid: false,
          message: typeof customResult === 'string' ? customResult : rule.message || 'Invalid value'
        };
      }
    }
    
    return { valid: true };
  }
  
  /**
   * Validate entire form
   * @returns {boolean} True if form is valid, false otherwise
   */
  validateForm() {
    const formData = new FormData(this.form);
    let isValid = true;
    this.errors = {};
    
    // Validate all fields with rules
    for (const fieldName in this.rules) {
      const value = formData.get(fieldName) || '';
      const result = this.validateField(fieldName, value);
      
      if (!result.valid) {
        this.errors[fieldName] = result.message;
        isValid = false;
      }
    }
    
    return isValid;
  }
  
  /**
   * Display error for a field
   * @param {string} fieldName - The name of the field
   * @param {string} message - The error message to display
   */
  showError(fieldName, message) {
    const field = this.form.querySelector(`[name="${fieldName}"]`);
    if (!field) return;
    
    const errorElement = field.parentElement.querySelector('.form-field__error');
    
    field.classList.add('is-invalid');
    field.classList.remove('is-valid');
    field.setAttribute('aria-invalid', 'true');
    
    if (errorElement) {
      errorElement.textContent = message;
      errorElement.setAttribute('role', 'alert');
    }
  }
  
  /**
   * Clear error for a field
   * @param {string} fieldName - The name of the field
   */
  clearError(fieldName) {
    const field = this.form.querySelector(`[name="${fieldName}"]`);
    if (!field) return;
    
    const errorElement = field.parentElement.querySelector('.form-field__error');
    
    field.classList.remove('is-invalid');
    field.classList.add('is-valid');
    field.setAttribute('aria-invalid', 'false');
    
    if (errorElement) {
      errorElement.textContent = '';
    }
  }
  
  /**
   * Clear all errors in the form
   */
  clearAllErrors() {
    for (const fieldName in this.rules) {
      this.clearError(fieldName);
    }
    this.errors = {};
  }
  
  /**
   * Initialize real-time validation
   * Sets up event listeners for blur events and form submission
   */
  init() {
    const fields = this.form.querySelectorAll('input, textarea, select');
    
    // Add blur event listeners for real-time validation
    fields.forEach(field => {
      // Validate on blur (when field loses focus)
      field.addEventListener('blur', (e) => {
        const fieldName = e.target.name;
        if (!fieldName || !this.rules[fieldName]) return;
        
        const result = this.validateField(fieldName, e.target.value);
        if (!result.valid) {
          this.showError(fieldName, result.message);
        } else {
          this.clearError(fieldName);
        }
      });
      
      // Clear error on input (as user types)
      field.addEventListener('input', (e) => {
        const fieldName = e.target.name;
        if (!fieldName || !this.rules[fieldName]) return;
        
        // Only clear error if field was previously invalid
        if (e.target.classList.contains('is-invalid')) {
          const result = this.validateField(fieldName, e.target.value);
          if (result.valid) {
            this.clearError(fieldName);
          }
        }
      });
    });
    
    // Prevent form submission if validation fails
    this.form.addEventListener('submit', (e) => {
      e.preventDefault();
      
      // Disable submit button during validation
      const submitButton = this.form.querySelector('[type="submit"]');
      if (submitButton) {
        submitButton.disabled = true;
      }
      
      if (this.validateForm()) {
        // Form is valid, allow submission
        // Re-enable button and submit
        if (submitButton) {
          submitButton.disabled = false;
        }
        
        // If there's a custom submit handler, call it
        if (this.onSubmit && typeof this.onSubmit === 'function') {
          this.onSubmit(new FormData(this.form));
        } else {
          // Otherwise, submit the form normally
          this.form.submit();
        }
      } else {
        // Form is invalid, show all errors and focus first error
        let firstErrorField = null;
        
        for (const [fieldName, message] of Object.entries(this.errors)) {
          this.showError(fieldName, message);
          
          if (!firstErrorField) {
            firstErrorField = this.form.querySelector(`[name="${fieldName}"]`);
          }
        }
        
        // Focus on first error field
        if (firstErrorField) {
          firstErrorField.focus();
        }
        
        // Re-enable submit button
        if (submitButton) {
          submitButton.disabled = false;
        }
      }
    });
  }
  
  /**
   * Set custom submit handler
   * @param {Function} handler - Function to call on successful validation
   */
  setSubmitHandler(handler) {
    this.onSubmit = handler;
  }
  
  /**
   * Format field name for display in error messages
   * @param {string} fieldName - The field name to format
   * @returns {string} Formatted field name
   * @private
   */
  formatFieldName(fieldName) {
    // Convert camelCase or snake_case to Title Case
    return fieldName
      .replace(/([A-Z])/g, ' $1')  // Add space before capital letters
      .replace(/_/g, ' ')           // Replace underscores with spaces
      .trim()                       // Remove leading/trailing spaces
      .split(' ')                   // Split into words
      .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase()) // Capitalize each word
      .join(' ');                   // Join back together
  }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
  module.exports = FormValidator;
}
