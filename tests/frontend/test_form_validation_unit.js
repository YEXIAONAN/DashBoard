/**
 * Unit tests for FormValidator class
 * Run with Node.js: node test_form_validation_unit.js
 */

// Mock DOM elements for testing
class MockElement {
    constructor(name) {
        this.name = name;
        this.classList = new Set();
        this.attributes = {};
    }
    
    classList = {
        add: (className) => this.classList.add(className),
        remove: (className) => this.classList.delete(className),
        contains: (className) => this.classList.has(className)
    };
    
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

// Load the FormValidator class
const fs = require('fs');
const vm = require('vm');

const code = fs.readFileSync('main/static/js/form-validation.js', 'utf8');
const sandbox = { module: { exports: {} }, exports: {} };
vm.createContext(sandbox);
vm.runInContext(code, sandbox);
const FormValidator = sandbox.module.exports;

// Test suite
console.log('Running FormValidator Unit Tests...\n');

let passedTests = 0;
let failedTests = 0;

function test(description, testFn) {
    try {
        testFn();
        console.log(`✓ ${description}`);
        passedTests++;
    } catch (error) {
        console.log(`✗ ${description}`);
        console.log(`  Error: ${error.message}`);
        failedTests++;
    }
}

function assert(condition, message) {
    if (!condition) {
        throw new Error(message || 'Assertion failed');
    }
}

function assertEquals(actual, expected, message) {
    if (JSON.stringify(actual) !== JSON.stringify(expected)) {
        throw new Error(message || `Expected ${JSON.stringify(expected)}, got ${JSON.stringify(actual)}`);
    }
}

// Test 1: Required field validation
test('validates required fields correctly', () => {
    const form = new MockForm();
    const validator = new FormValidator(form, {
        email: { required: true }
    });
    
    const result = validator.validateField('email', '');
    assert(!result.valid, 'Empty required field should be invalid');
    assert(result.message.includes('required'), 'Error message should mention required');
});

// Test 2: Email pattern validation
test('validates email pattern correctly', () => {
    const form = new MockForm();
    const validator = new FormValidator(form, {
        email: {
            pattern: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
            message: 'Invalid email'
        }
    });
    
    const invalidResult = validator.validateField('email', 'invalid-email');
    assert(!invalidResult.valid, 'Invalid email should fail validation');
    
    const validResult = validator.validateField('email', 'test@example.com');
    assert(validResult.valid, 'Valid email should pass validation');
});

// Test 3: MinLength validation
test('validates minLength correctly', () => {
    const form = new MockForm();
    const validator = new FormValidator(form, {
        password: {
            minLength: 8,
            message: 'Password too short'
        }
    });
    
    const shortResult = validator.validateField('password', 'short');
    assert(!shortResult.valid, 'Short password should fail validation');
    
    const longResult = validator.validateField('password', 'longenough');
    assert(longResult.valid, 'Long enough password should pass validation');
});

// Test 4: MaxLength validation
test('validates maxLength correctly', () => {
    const form = new MockForm();
    const validator = new FormValidator(form, {
        username: {
            maxLength: 10,
            message: 'Username too long'
        }
    });
    
    const longResult = validator.validateField('username', 'verylongusername');
    assert(!longResult.valid, 'Long username should fail validation');
    
    const shortResult = validator.validateField('username', 'short');
    assert(shortResult.valid, 'Short username should pass validation');
});

// Test 5: Min value validation
test('validates min value correctly', () => {
    const form = new MockForm();
    const validator = new FormValidator(form, {
        quantity: {
            min: 1,
            message: 'Minimum 1'
        }
    });
    
    const lowResult = validator.validateField('quantity', '0');
    assert(!lowResult.valid, 'Value below minimum should fail validation');
    
    const validResult = validator.validateField('quantity', '5');
    assert(validResult.valid, 'Value above minimum should pass validation');
});

// Test 6: Max value validation
test('validates max value correctly', () => {
    const form = new MockForm();
    const validator = new FormValidator(form, {
        quantity: {
            max: 99,
            message: 'Maximum 99'
        }
    });
    
    const highResult = validator.validateField('quantity', '100');
    assert(!highResult.valid, 'Value above maximum should fail validation');
    
    const validResult = validator.validateField('quantity', '50');
    assert(validResult.valid, 'Value below maximum should pass validation');
});

// Test 7: Optional field validation
test('validates optional fields correctly', () => {
    const form = new MockForm();
    const validator = new FormValidator(form, {
        phone: {
            required: false,
            pattern: /^\d{10}$/,
            message: 'Invalid phone'
        }
    });
    
    const emptyResult = validator.validateField('phone', '');
    assert(emptyResult.valid, 'Empty optional field should be valid');
    
    const invalidResult = validator.validateField('phone', 'abc');
    assert(!invalidResult.valid, 'Invalid optional field should fail validation');
    
    const validResult = validator.validateField('phone', '1234567890');
    assert(validResult.valid, 'Valid optional field should pass validation');
});

// Test 8: Custom validator function
test('validates with custom validator function', () => {
    const form = new MockForm();
    const validator = new FormValidator(form, {
        age: {
            validator: (value) => {
                const age = parseInt(value);
                return age >= 18 && age <= 100 ? true : 'Age must be between 18 and 100';
            }
        }
    });
    
    const youngResult = validator.validateField('age', '15');
    assert(!youngResult.valid, 'Age below 18 should fail validation');
    
    const validResult = validator.validateField('age', '25');
    assert(validResult.valid, 'Valid age should pass validation');
});

// Test 9: Field name formatting
test('formats field names correctly', () => {
    const form = new MockForm();
    const validator = new FormValidator(form, {
        emailAddress: { required: true },
        user_name: { required: true }
    });
    
    const camelCaseResult = validator.validateField('emailAddress', '');
    assert(camelCaseResult.message.includes('Email Address'), 'Should format camelCase correctly');
    
    const snakeCaseResult = validator.validateField('user_name', '');
    assert(snakeCaseResult.message.includes('User Name'), 'Should format snake_case correctly');
});

// Test 10: Multiple validation rules
test('validates multiple rules correctly', () => {
    const form = new MockForm();
    const validator = new FormValidator(form, {
        password: {
            required: true,
            minLength: 8,
            pattern: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/,
            message: 'Password must contain uppercase, lowercase, and number'
        }
    });
    
    const emptyResult = validator.validateField('password', '');
    assert(!emptyResult.valid, 'Empty password should fail required check');
    
    const shortResult = validator.validateField('password', 'Short1');
    assert(!shortResult.valid, 'Short password should fail minLength check');
    
    const weakResult = validator.validateField('password', 'weakpassword');
    assert(!weakResult.valid, 'Weak password should fail pattern check');
    
    const validResult = validator.validateField('password', 'StrongPass123');
    assert(validResult.valid, 'Strong password should pass all checks');
});

// Print summary
console.log('\n' + '='.repeat(50));
console.log(`Tests passed: ${passedTests}`);
console.log(`Tests failed: ${failedTests}`);
console.log(`Total tests: ${passedTests + failedTests}`);
console.log('='.repeat(50));

if (failedTests === 0) {
    console.log('\n✓ All tests passed!');
    process.exit(0);
} else {
    console.log('\n✗ Some tests failed!');
    process.exit(1);
}
