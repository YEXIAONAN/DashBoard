/**
 * Property-Based Test for Form Validation Round Trip
 * Feature: frontend-ui-optimization
 * Property 5: Form validation round trip
 * 
 * **Validates: Requirements 6.1, 6.3, 6.7**
 * 
 * This test validates that valid form data always passes validation without errors.
 * The "round trip" property ensures that:
 * 1. Valid data is entered
 * 2. Validation is performed
 * 3. The data passes validation
 * 4. The form can be submitted without errors
 * 
 * Run with: node test_form_validation_roundtrip.js
 */

const fc = require('fast-check');

// Mock FormData for testing
class MockFormData {
    constructor(form) {
        this.data = new Map();
        if (form && form.data) {
            for (const [name, value] of Object.entries(form.data)) {
                this.data.set(name, value);
            }
        }
    }
    
    get(name) {
        return this.data.get(name) || '';
    }
    
    entries() {
        return this.data.entries();
    }
}

// Load FormValidator using a simpler approach
// Read the file and execute it in a function context
const fs = require('fs');
const vm = require('vm');

const code = fs.readFileSync('main/static/js/form-validation.js', 'utf8');
const sandbox = { 
    module: { exports: {} }, 
    exports: {},
    FormData: MockFormData  // Make FormData available in the sandbox
};
vm.createContext(sandbox);
vm.runInContext(code, sandbox);
const FormValidator = sandbox.module.exports;

// Mock DOM elements for testing
class MockElement {
    constructor(name, value = '') {
        this.name = name;
        this.value = value;
        this._classList = new Set();
        this.attributes = {};
        this.parentElement = {
            querySelector: (selector) => {
                if (selector === '.form-field__error') {
                    return { 
                        textContent: '', 
                        setAttribute: () => {},
                        getAttribute: () => null
                    };
                }
                return null;
            }
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
    
    focus() {
        // Mock focus
    }
}

class MockForm {
    constructor(data = {}) {
        this.fields = {};
        this.submitted = false;
        this.data = data;
        
        // Create mock fields for each data entry
        for (const [name, value] of Object.entries(data)) {
            this.fields[name] = new MockElement(name, value);
        }
    }
    
    querySelector(selector) {
        const match = selector.match(/\[name="([^"]+)"\]/);
        if (match) {
            if (!this.fields[match[1]]) {
                this.fields[match[1]] = new MockElement(match[1]);
            }
            return this.fields[match[1]];
        }
        
        // Handle submit button selector
        if (selector === '[type="submit"]') {
            return {
                disabled: false,
                focus: () => {}
            };
        }
        
        return null;
    }
    
    querySelectorAll(selector) {
        if (selector === 'input, textarea, select') {
            return Object.values(this.fields);
        }
        return [];
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
    },
    age: {
        required: false,
        min: 18,
        max: 120,
        message: 'Age must be between 18 and 120'
    }
};

console.log('='.repeat(70));
console.log('Property-Based Test for Form Validation Round Trip');
console.log('Feature: frontend-ui-optimization, Property 5: Form validation round trip');
console.log('**Validates: Requirements 6.1, 6.3, 6.7**');
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
// Property 5.1: Valid email data always passes validation round trip
// ============================================================================
runPropertyTest(
    'Valid email data always passes validation round trip',
    fc.property(
        fc.tuple(
            fc.stringOf(fc.constantFrom(...'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'.split('')), { minLength: 1, maxLength: 10 }),
            fc.stringOf(fc.constantFrom(...'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'.split('')), { minLength: 1, maxLength: 10 }),
            fc.stringOf(fc.constantFrom(...'abcdefghijklmnopqrstuvwxyz'.split('')), { minLength: 2, maxLength: 5 })
        ).map(([local, domain, tld]) => `${local}@${domain}.${tld}`),
        (validEmail) => {
            const formData = { email: validEmail };
            const form = new MockForm(formData);
            const validator = new FormValidator(form, { email: validationRules.email });
            
            // Step 1: Validate the field
            const fieldResult = validator.validateField('email', validEmail);
            
            // Step 2: Validate the entire form
            const formResult = validator.validateForm();
            
            // Step 3: Check that validation passed
            // Valid data should pass both field and form validation
            return fieldResult.valid === true && 
                   formResult === true && 
                   Object.keys(validator.errors).length === 0;
        }
    ),
    { numRuns: 100 }
);

// ============================================================================
// Property 5.2: Valid password data always passes validation round trip
// ============================================================================
runPropertyTest(
    'Valid password data always passes validation round trip',
    fc.property(
        fc.stringOf(
            fc.constantFrom(...'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*'.split('')),
            { minLength: 8, maxLength: 20 }
        ).filter(s => /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/.test(s)),
        (validPassword) => {
            const formData = { password: validPassword };
            const form = new MockForm(formData);
            const validator = new FormValidator(form, { password: validationRules.password });
            
            // Step 1: Validate the field
            const fieldResult = validator.validateField('password', validPassword);
            
            // Step 2: Validate the entire form
            const formResult = validator.validateForm();
            
            // Step 3: Check that validation passed
            return fieldResult.valid === true && 
                   formResult === true && 
                   Object.keys(validator.errors).length === 0;
        }
    ),
    { numRuns: 100 }
);

// ============================================================================
// Property 5.3: Valid quantity data always passes validation round trip
// ============================================================================
runPropertyTest(
    'Valid quantity data always passes validation round trip',
    fc.property(
        fc.integer({ min: 1, max: 99 }),
        (validQuantity) => {
            const formData = { quantity: validQuantity.toString() };
            const form = new MockForm(formData);
            const validator = new FormValidator(form, { quantity: validationRules.quantity });
            
            // Step 1: Validate the field
            const fieldResult = validator.validateField('quantity', validQuantity.toString());
            
            // Step 2: Validate the entire form
            const formResult = validator.validateForm();
            
            // Step 3: Check that validation passed
            return fieldResult.valid === true && 
                   formResult === true && 
                   Object.keys(validator.errors).length === 0;
        }
    ),
    { numRuns: 100 }
);

// ============================================================================
// Property 5.4: Valid username data always passes validation round trip
// ============================================================================
runPropertyTest(
    'Valid username data always passes validation round trip',
    fc.property(
        fc.stringOf(
            fc.constantFrom(...'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_'.split('')),
            { minLength: 3, maxLength: 20 }
        ).filter(s => /^[a-zA-Z0-9_]+$/.test(s) && s.length >= 3),
        (validUsername) => {
            const formData = { username: validUsername };
            const form = new MockForm(formData);
            const validator = new FormValidator(form, { username: validationRules.username });
            
            // Step 1: Validate the field
            const fieldResult = validator.validateField('username', validUsername);
            
            // Step 2: Validate the entire form
            const formResult = validator.validateForm();
            
            // Step 3: Check that validation passed
            return fieldResult.valid === true && 
                   formResult === true && 
                   Object.keys(validator.errors).length === 0;
        }
    ),
    { numRuns: 100 }
);

// ============================================================================
// Property 5.5: Valid optional field data always passes validation round trip
// ============================================================================
runPropertyTest(
    'Valid optional field data (phone) always passes validation round trip',
    fc.property(
        fc.oneof(
            fc.constant(''),  // Empty is valid for optional fields
            fc.stringOf(fc.constantFrom(...'0123456789'.split('')), { minLength: 10, maxLength: 11 })
        ),
        (validPhone) => {
            const formData = { phone: validPhone };
            const form = new MockForm(formData);
            const validator = new FormValidator(form, { phone: validationRules.phone });
            
            // Step 1: Validate the field
            const fieldResult = validator.validateField('phone', validPhone);
            
            // Step 2: Validate the entire form
            const formResult = validator.validateForm();
            
            // Step 3: Check that validation passed
            return fieldResult.valid === true && 
                   formResult === true && 
                   Object.keys(validator.errors).length === 0;
        }
    ),
    { numRuns: 100 }
);

// ============================================================================
// Property 5.6: Complete valid form data always passes validation round trip
// ============================================================================
runPropertyTest(
    'Complete valid form data always passes validation round trip',
    fc.property(
        fc.record({
            email: fc.tuple(
                fc.stringOf(fc.constantFrom(...'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'.split('')), { minLength: 1, maxLength: 10 }),
                fc.stringOf(fc.constantFrom(...'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'.split('')), { minLength: 1, maxLength: 10 }),
                fc.stringOf(fc.constantFrom(...'abcdefghijklmnopqrstuvwxyz'.split('')), { minLength: 2, maxLength: 5 })
            ).map(([local, domain, tld]) => `${local}@${domain}.${tld}`),
            password: fc.stringOf(
                fc.constantFrom(...'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*'.split('')),
                { minLength: 8, maxLength: 20 }
            ).filter(s => /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/.test(s)),
            quantity: fc.integer({ min: 1, max: 99 }),
            username: fc.stringOf(
                fc.constantFrom(...'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_'.split('')),
                { minLength: 3, maxLength: 20 }
            ).filter(s => /^[a-zA-Z0-9_]+$/.test(s) && s.length >= 3)
        }),
        (validData) => {
            const formData = {
                email: validData.email,
                password: validData.password,
                quantity: validData.quantity.toString(),
                username: validData.username
            };
            const form = new MockForm(formData);
            const validator = new FormValidator(form, validationRules);
            
            // Step 1: Validate each field individually
            const emailResult = validator.validateField('email', validData.email);
            const passwordResult = validator.validateField('password', validData.password);
            const quantityResult = validator.validateField('quantity', validData.quantity.toString());
            const usernameResult = validator.validateField('username', validData.username);
            
            // Step 2: Validate the entire form
            const formResult = validator.validateForm();
            
            // Step 3: Check that all validations passed
            return emailResult.valid === true && 
                   passwordResult.valid === true && 
                   quantityResult.valid === true && 
                   usernameResult.valid === true &&
                   formResult === true && 
                   Object.keys(validator.errors).length === 0;
        }
    ),
    { numRuns: 100 }
);

// ============================================================================
// Property 5.7: Valid form with optional fields always passes validation
// ============================================================================
runPropertyTest(
    'Valid form with optional fields always passes validation round trip',
    fc.property(
        fc.record({
            email: fc.tuple(
                fc.stringOf(fc.constantFrom(...'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'.split('')), { minLength: 1, maxLength: 10 }),
                fc.stringOf(fc.constantFrom(...'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'.split('')), { minLength: 1, maxLength: 10 }),
                fc.stringOf(fc.constantFrom(...'abcdefghijklmnopqrstuvwxyz'.split('')), { minLength: 2, maxLength: 5 })
            ).map(([local, domain, tld]) => `${local}@${domain}.${tld}`),
            password: fc.stringOf(
                fc.constantFrom(...'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*'.split('')),
                { minLength: 8, maxLength: 20 }
            ).filter(s => /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/.test(s)),
            phone: fc.oneof(
                fc.constant(''),
                fc.stringOf(fc.constantFrom(...'0123456789'.split('')), { minLength: 10, maxLength: 11 })
            ),
            age: fc.oneof(
                fc.constant(''),
                fc.integer({ min: 18, max: 120 }).map(n => n.toString())
            )
        }),
        (validData) => {
            const formData = {
                email: validData.email,
                password: validData.password,
                phone: validData.phone,
                age: validData.age
            };
            const form = new MockForm(formData);
            const validator = new FormValidator(form, {
                email: validationRules.email,
                password: validationRules.password,
                phone: validationRules.phone,
                age: validationRules.age
            });
            
            // Step 1: Validate each field individually
            const emailResult = validator.validateField('email', validData.email);
            const passwordResult = validator.validateField('password', validData.password);
            const phoneResult = validator.validateField('phone', validData.phone);
            const ageResult = validator.validateField('age', validData.age);
            
            // Step 2: Validate the entire form
            const formResult = validator.validateForm();
            
            // Step 3: Check that all validations passed
            return emailResult.valid === true && 
                   passwordResult.valid === true && 
                   phoneResult.valid === true && 
                   ageResult.valid === true &&
                   formResult === true && 
                   Object.keys(validator.errors).length === 0;
        }
    ),
    { numRuns: 100 }
);

// ============================================================================
// Property 5.8: Validation is idempotent (multiple validations = same result)
// ============================================================================
runPropertyTest(
    'Validation is idempotent (validating same data multiple times gives same result)',
    fc.property(
        fc.record({
            email: fc.tuple(
                fc.stringOf(fc.constantFrom(...'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'.split('')), { minLength: 1, maxLength: 10 }),
                fc.stringOf(fc.constantFrom(...'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'.split('')), { minLength: 1, maxLength: 10 }),
                fc.stringOf(fc.constantFrom(...'abcdefghijklmnopqrstuvwxyz'.split('')), { minLength: 2, maxLength: 5 })
            ).map(([local, domain, tld]) => `${local}@${domain}.${tld}`),
            password: fc.stringOf(
                fc.constantFrom(...'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*'.split('')),
                { minLength: 8, maxLength: 20 }
            ).filter(s => /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/.test(s))
        }),
        (validData) => {
            const formData = {
                email: validData.email,
                password: validData.password
            };
            const form = new MockForm(formData);
            const validator = new FormValidator(form, {
                email: validationRules.email,
                password: validationRules.password
            });
            
            // Validate the form multiple times
            const result1 = validator.validateForm();
            const errors1 = { ...validator.errors };
            
            const result2 = validator.validateForm();
            const errors2 = { ...validator.errors };
            
            const result3 = validator.validateForm();
            const errors3 = { ...validator.errors };
            
            // All results should be identical
            return result1 === result2 && 
                   result2 === result3 && 
                   JSON.stringify(errors1) === JSON.stringify(errors2) &&
                   JSON.stringify(errors2) === JSON.stringify(errors3);
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
    console.log('Form validation round trip property is verified:');
    console.log('  - Valid data always passes validation');
    console.log('  - Forms with valid data can be submitted without errors');
    console.log('  - Validation is consistent and idempotent');
    process.exit(0);
} else {
    console.log(`\n✗ ${failedTests} property test(s) failed!`);
    console.log('Form validation round trip has issues that need to be addressed.');
    process.exit(1);
}
