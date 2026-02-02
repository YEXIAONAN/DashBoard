/**
 * Property-Based Tests for FormValidator class
 * Feature: frontend-ui-optimization
 * Property 1: Form validation consistency
 * 
 * **Validates: Requirements 6.2, 6.3, 6.4**
 * 
 * This test validates that form validation rules work consistently across all input types.
 * Invalid data should always fail validation, and valid data should always pass.
 * 
 * Run with: npm test
 */

const fc = require('fast-check');

// Load FormValidator using a simpler approach
// Read the file and execute it in a function context
const fs = require('fs');
const vm = require('vm');

const code = fs.readFileSync('main/static/js/form-validation.js', 'utf8');
const sandbox = { module: { exports: {} }, exports: {} };
vm.createContext(sandbox);
vm.runInContext(code, sandbox);
const FormValidator = sandbox.module.exports;

// Mock DOM elements for testing
class MockElement {
    constructor(name) {
        this.name = name;
        this._classList = new Set();
        this.attributes = {};
        this.parentElement = {
            querySelector: () => ({ textContent: '', setAttribute: () => {} })
        };
    }
    
    get classList() {
        return {
            add: (className) => this._classList.add(className),
            remove: (className) => this._classList.delete(className),
            contains: (className) => this._classList.has(className)
        };
    }
    
    setAttribute(name, value) {
        this.attributes[name] = value;
    }
    
    getAttribute(name) {
        return this.attributes[name];
    }
}

class MockForm {
    constructor() {
        this.fields = {};
        this.submitted = false;
    }
    
    querySelector(selector) {
        const match = selector.match(/\[name="([^"]+)"\]/);
        if (match) {
            if (!this.fields[match[1]]) {
                this.fields[match[1]] = new MockElement(match[1]);
            }
            return this.fields[match[1]];
        }
        return null;
    }
    
    querySelectorAll() {
        return Object.values(this.fields);
    }
    
    addEventListener(event, handler) {
        this[`on${event}`] = handler;
    }
    
    submit() {
        this.submitted = true;
    }
}

// Validation rules for testing
const validationRules = {
    email: {
        required: true,
        // Strict email pattern that rejects double dots, leading/trailing dots, and other invalid patterns
        // Pattern breakdown:
        // - Local part: starts with alphanumeric, can contain dots/underscores/hyphens (but not consecutive), ends with alphanumeric
        // - Domain: starts with alphanumeric, can contain hyphens, ends with alphanumeric
        // - TLD: at least one dot followed by 2+ letter TLD
        pattern: /^[a-zA-Z0-9]+([._-][a-zA-Z0-9]+)*@[a-zA-Z0-9]+(-[a-zA-Z0-9]+)*(\.[a-zA-Z0-9]+(-[a-zA-Z0-9]+)*)+$/,
        message: 'Please enter a valid email address'
    },
    password: {
        required: true,
        minLength: 8,
        pattern: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/,
        message: 'Password must contain uppercase, lowercase, and number'
    },
    phone: {
        required: false,
        pattern: /^\d{10,11}$/,
        message: 'Please enter a valid phone number'
    },
    quantity: {
        required: true,
        min: 1,
        max: 99,
        message: 'Quantity must be between 1 and 99'
    },
    username: {
        required: true,
        minLength: 3,
        maxLength: 20,
        pattern: /^[a-zA-Z0-9_]+$/,
        message: 'Username must be 3-20 alphanumeric characters'
    }
};

console.log('='.repeat(70));
console.log('Property-Based Tests for Form Validation Consistency');
console.log('Feature: frontend-ui-optimization, Property 1: Form validation consistency');
console.log('**Validates: Requirements 6.2, 6.3, 6.4**');
console.log('='.repeat(70));
console.log('');

let totalTests = 0;
let passedTests = 0;
let failedTests = 0;

function runPropertyTest(description, property, options = {}) {
    totalTests++;
    console.log(`\nTest ${totalTests}: ${description}`);
    console.log('-'.repeat(70));
    
    try {
        fc.assert(property, { 
            numRuns: options.numRuns || 100,
            verbose: options.verbose || false
        });
        console.log(`✓ PASSED (${options.numRuns || 100} iterations)`);
        passedTests++;
        return true;
    } catch (error) {
        console.log(`✗ FAILED`);
        console.log(`  Error: ${error.message}`);
        if (error.counterexample) {
            console.log(`  Counterexample: ${JSON.stringify(error.counterexample)}`);
        }
        failedTests++;
        return false;
    }
}

// ============================================================================
// Property 1.1: Invalid email addresses always fail validation
// ============================================================================
runPropertyTest(
    'Invalid email addresses always fail validation',
    fc.property(
        fc.oneof(
            fc.constant(''),                          // Empty string
            fc.constant('invalid'),                   // No @ symbol
            fc.constant('invalid@'),                  // No domain
            fc.constant('@invalid.com'),              // No local part
            fc.constant('invalid@domain'),            // No TLD
            fc.constant('invalid @domain.com'),       // Space in email
            fc.constant('invalid..email@domain.com'), // Double dots
            fc.constant('.invalid@domain.com'),       // Starts with dot
            fc.constant('invalid.@domain.com'),       // Ends with dot before @
            fc.string().filter(s => s.length > 0 && !validationRules.email.pattern.test(s)) // Random invalid
        ),
        (invalidEmail) => {
            const form = new MockForm();
            const validator = new FormValidator(form, validationRules);
            const result = validator.validateField('email', invalidEmail);
            
            // Invalid emails should always fail validation
            return result.valid === false && typeof result.message === 'string' && result.message.length > 0;
        }
    ),
    { numRuns: 100 }
);

// ============================================================================
// Property 1.2: Valid email addresses always pass validation
// ============================================================================
runPropertyTest(
    'Valid email addresses always pass validation',
    fc.property(
        // Custom email generator that matches our validation pattern
        fc.tuple(
            fc.stringOf(fc.constantFrom(...'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'.split('')), { minLength: 1, maxLength: 10 }),
            fc.stringOf(fc.constantFrom(...'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'.split('')), { minLength: 1, maxLength: 10 }),
            fc.stringOf(fc.constantFrom(...'abcdefghijklmnopqrstuvwxyz'.split('')), { minLength: 2, maxLength: 5 })
        ).map(([local, domain, tld]) => `${local}@${domain}.${tld}`),
        (validEmail) => {
            const form = new MockForm();
            const validator = new FormValidator(form, validationRules);
            const result = validator.validateField('email', validEmail);
            
            // Valid emails should always pass validation
            return result.valid === true;
        }
    ),
    { numRuns: 100 }
);

// ============================================================================
// Property 1.3: Passwords shorter than minLength always fail validation
// ============================================================================
runPropertyTest(
    'Passwords shorter than minLength always fail validation',
    fc.property(
        fc.string({ maxLength: 7 }), // Shorter than required 8 characters
        (shortPassword) => {
            const form = new MockForm();
            const validator = new FormValidator(form, validationRules);
            const result = validator.validateField('password', shortPassword);
            
            // Short passwords should always fail validation
            return result.valid === false && result.message.length > 0;
        }
    ),
    { numRuns: 100 }
);

// ============================================================================
// Property 1.4: Passwords without required pattern always fail validation
// ============================================================================
runPropertyTest(
    'Passwords without required pattern always fail validation',
    fc.property(
        fc.oneof(
            fc.string({ minLength: 8 }).filter(s => !/[A-Z]/.test(s)), // No uppercase
            fc.string({ minLength: 8 }).filter(s => !/[a-z]/.test(s)), // No lowercase
            fc.string({ minLength: 8 }).filter(s => !/\d/.test(s))     // No digit
        ),
        (weakPassword) => {
            const form = new MockForm();
            const validator = new FormValidator(form, validationRules);
            const result = validator.validateField('password', weakPassword);
            
            // Weak passwords should always fail validation
            return result.valid === false && result.message.length > 0;
        }
    ),
    { numRuns: 100 }
);

// ============================================================================
// Property 1.5: Valid passwords always pass validation
// ============================================================================
runPropertyTest(
    'Valid passwords always pass validation',
    fc.property(
        fc.string({ minLength: 8, maxLength: 20 })
            .filter(s => /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/.test(s)),
        (validPassword) => {
            const form = new MockForm();
            const validator = new FormValidator(form, validationRules);
            const result = validator.validateField('password', validPassword);
            
            // Valid passwords should always pass validation
            return result.valid === true;
        }
    ),
    { numRuns: 100 }
);

// ============================================================================
// Property 1.6: Quantity values outside min/max range always fail validation
// ============================================================================
runPropertyTest(
    'Quantity values outside min/max range always fail validation',
    fc.property(
        fc.oneof(
            fc.integer({ max: 0 }),      // Below minimum
            fc.integer({ min: 100 })     // Above maximum
        ),
        (invalidQuantity) => {
            const form = new MockForm();
            const validator = new FormValidator(form, validationRules);
            const result = validator.validateField('quantity', invalidQuantity.toString());
            
            // Out-of-range quantities should always fail validation
            return result.valid === false && result.message.length > 0;
        }
    ),
    { numRuns: 100 }
);

// ============================================================================
// Property 1.7: Quantity values within min/max range always pass validation
// ============================================================================
runPropertyTest(
    'Quantity values within min/max range always pass validation',
    fc.property(
        fc.integer({ min: 1, max: 99 }),
        (validQuantity) => {
            const form = new MockForm();
            const validator = new FormValidator(form, validationRules);
            const result = validator.validateField('quantity', validQuantity.toString());
            
            // Valid quantities should always pass validation
            return result.valid === true;
        }
    ),
    { numRuns: 100 }
);

// ============================================================================
// Property 1.8: Optional fields with empty values always pass validation
// ============================================================================
runPropertyTest(
    'Optional fields with empty values always pass validation',
    fc.property(
        fc.constantFrom('', '   ', '\t', '\n'),
        (emptyValue) => {
            const form = new MockForm();
            const validator = new FormValidator(form, validationRules);
            const result = validator.validateField('phone', emptyValue);
            
            // Empty optional fields should always pass validation
            return result.valid === true;
        }
    ),
    { numRuns: 100 }
);

// ============================================================================
// Property 1.9: Optional fields with invalid non-empty values always fail
// ============================================================================
runPropertyTest(
    'Optional fields with invalid non-empty values always fail validation',
    fc.property(
        fc.string({ minLength: 1 }).filter(s => !/^\d{10,11}$/.test(s.trim())),
        (invalidPhone) => {
            const form = new MockForm();
            const validator = new FormValidator(form, validationRules);
            const result = validator.validateField('phone', invalidPhone);
            
            // Invalid non-empty optional fields should fail validation
            return result.valid === false && result.message.length > 0;
        }
    ),
    { numRuns: 100 }
);

// ============================================================================
// Property 1.10: Username length constraints are enforced consistently
// ============================================================================
runPropertyTest(
    'Username length constraints are enforced consistently',
    fc.property(
        fc.oneof(
            fc.string({ maxLength: 2 }),      // Too short
            fc.string({ minLength: 21 })      // Too long
        ).filter(s => /^[a-zA-Z0-9_]*$/.test(s)), // Valid characters
        (invalidUsername) => {
            const form = new MockForm();
            const validator = new FormValidator(form, validationRules);
            const result = validator.validateField('username', invalidUsername);
            
            // Usernames with invalid length should fail validation
            return result.valid === false && result.message.length > 0;
        }
    ),
    { numRuns: 100 }
);

// ============================================================================
// Property 1.11: Multiple validation rules are applied consistently
// ============================================================================
runPropertyTest(
    'Multiple validation rules are applied consistently',
    fc.property(
        fc.record({
            email: fc.tuple(
                fc.stringOf(fc.constantFrom(...'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'.split('')), { minLength: 1, maxLength: 10 }),
                fc.stringOf(fc.constantFrom(...'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'.split('')), { minLength: 1, maxLength: 10 }),
                fc.stringOf(fc.constantFrom(...'abcdefghijklmnopqrstuvwxyz'.split('')), { minLength: 2, maxLength: 5 })
            ).map(([local, domain, tld]) => `${local}@${domain}.${tld}`),
            password: fc.stringOf(
                fc.constantFrom(...'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'.split('')),
                { minLength: 8, maxLength: 20 }
            ).filter(s => /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/.test(s)),
            quantity: fc.integer({ min: 1, max: 99 }),
            username: fc.stringOf(
                fc.constantFrom(...'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_'.split('')),
                { minLength: 3, maxLength: 20 }
            ).filter(s => /^[a-zA-Z0-9_]+$/.test(s) && s.length >= 3)
        }),
        (validData) => {
            const form = new MockForm();
            const validator = new FormValidator(form, validationRules);
            
            // All valid fields should pass validation
            const emailResult = validator.validateField('email', validData.email);
            const passwordResult = validator.validateField('password', validData.password);
            const quantityResult = validator.validateField('quantity', validData.quantity.toString());
            const usernameResult = validator.validateField('username', validData.username);
            
            return emailResult.valid && 
                   passwordResult.valid && 
                   quantityResult.valid && 
                   usernameResult.valid;
        }
    ),
    { numRuns: 100 }
);

// ============================================================================
// Property 1.12: Validation results are deterministic
// ============================================================================
runPropertyTest(
    'Validation results are deterministic (same input = same output)',
    fc.property(
        fc.string(),
        fc.constantFrom('email', 'password', 'phone', 'quantity', 'username'),
        (value, fieldName) => {
            const form = new MockForm();
            const validator = new FormValidator(form, validationRules);
            
            // Validate the same field twice with the same value
            const result1 = validator.validateField(fieldName, value);
            const result2 = validator.validateField(fieldName, value);
            
            // Results should be identical
            return result1.valid === result2.valid && 
                   result1.message === result2.message;
        }
    ),
    { numRuns: 100 }
);

// Print summary
console.log('\n' + '='.repeat(70));
console.log('SUMMARY');
console.log('='.repeat(70));
console.log(`Total property tests: ${totalTests}`);
console.log(`Passed: ${passedTests} (${Math.round(passedTests/totalTests*100)}%)`);
console.log(`Failed: ${failedTests} (${Math.round(failedTests/totalTests*100)}%)`);
console.log(`Total iterations: ${totalTests * 100} (100 per property)`);
console.log('='.repeat(70));

if (failedTests === 0) {
    console.log('\n✓ All property tests passed!');
    console.log('Form validation consistency is verified across all input types.');
    process.exit(0);
} else {
    console.log(`\n✗ ${failedTests} property test(s) failed!`);
    console.log('Form validation has inconsistencies that need to be addressed.');
    process.exit(1);
}
