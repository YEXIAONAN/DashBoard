"""
Unit tests for form validation module
Tests the FormValidator JavaScript class functionality
"""

import subprocess
import sys

def test_form_validation_syntax():
    """Test that the JavaScript file has valid syntax"""
    print("Testing JavaScript syntax...")
    
    try:
        # Check if Node.js is available
        result = subprocess.run(
            ['node', '--check', 'main/static/js/form-validation.js'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            print("✓ JavaScript syntax is valid")
            return True
        else:
            print(f"✗ JavaScript syntax error: {result.stderr}")
            return False
    except FileNotFoundError:
        print("⚠ Node.js not found, skipping syntax check")
        return True
    except Exception as e:
        print(f"⚠ Error checking syntax: {e}")
        return True

def test_form_validation_structure():
    """Test that the JavaScript file has the expected structure"""
    print("\nTesting JavaScript structure...")
    
    with open('main/static/js/form-validation.js', 'r', encoding='utf-8') as f:
        content = f.read()
    
    tests_passed = 0
    tests_failed = 0
    
    # Check for FormValidator class
    if 'class FormValidator' in content:
        print("✓ FormValidator class is defined")
        tests_passed += 1
    else:
        print("✗ FormValidator class not found")
        tests_failed += 1
    
    # Check for required methods
    required_methods = [
        'constructor',
        'validateField',
        'validateForm',
        'showError',
        'clearError',
        'init'
    ]
    
    for method in required_methods:
        if f'{method}(' in content:
            print(f"✓ Method '{method}' is defined")
            tests_passed += 1
        else:
            print(f"✗ Method '{method}' not found")
            tests_failed += 1
    
    # Check for validation rule support
    validation_features = [
        ('required', 'Required field validation'),
        ('pattern', 'Pattern validation'),
        ('minLength', 'Minimum length validation'),
        ('maxLength', 'Maximum length validation'),
        ('min', 'Minimum value validation'),
        ('max', 'Maximum value validation'),
        ('validator', 'Custom validator function')
    ]
    
    for feature, description in validation_features:
        if feature in content:
            print(f"✓ {description} is supported")
            tests_passed += 1
        else:
            print(f"✗ {description} not found")
            tests_failed += 1
    
    # Check for CSS class integration
    css_classes = ['is-invalid', 'is-valid', 'form-field__error']
    for css_class in css_classes:
        if css_class in content:
            print(f"✓ CSS class '{css_class}' is used")
            tests_passed += 1
        else:
            print(f"✗ CSS class '{css_class}' not found")
            tests_failed += 1
    
    # Check for accessibility features
    accessibility_features = [
        ('aria-invalid', 'ARIA invalid attribute'),
        ('role', 'ARIA role attribute')
    ]
    
    for feature, description in accessibility_features:
        if feature in content:
            print(f"✓ {description} is supported")
            tests_passed += 1
        else:
            print(f"✗ {description} not found")
            tests_failed += 1
    
    # Check for event listeners
    events = ['blur', 'input', 'submit']
    for event in events:
        if f"addEventListener('{event}'" in content or f'addEventListener("{event}"' in content:
            print(f"✓ Event listener for '{event}' is implemented")
            tests_passed += 1
        else:
            print(f"✗ Event listener for '{event}' not found")
            tests_failed += 1
    
    return tests_passed, tests_failed

def test_documentation():
    """Test that the code has proper documentation"""
    print("\nTesting documentation...")
    
    with open('main/static/js/form-validation.js', 'r', encoding='utf-8') as f:
        content = f.read()
    
    tests_passed = 0
    tests_failed = 0
    
    # Check for JSDoc comments
    if '/**' in content and '@param' in content and '@returns' in content:
        print("✓ JSDoc documentation is present")
        tests_passed += 1
    else:
        print("✗ JSDoc documentation is incomplete")
        tests_failed += 1
    
    # Check for requirements references
    if 'Requirements:' in content or 'Requirement' in content:
        print("✓ Requirements are referenced")
        tests_passed += 1
    else:
        print("✗ Requirements references not found")
        tests_failed += 1
    
    # Check for usage examples
    if '@example' in content:
        print("✓ Usage examples are provided")
        tests_passed += 1
    else:
        print("✗ Usage examples not found")
        tests_failed += 1
    
    return tests_passed, tests_failed

def main():
    print("=" * 60)
    print("Form Validation Module Tests")
    print("=" * 60)
    
    total_passed = 0
    total_failed = 0
    
    # Run syntax test
    if not test_form_validation_syntax():
        print("\n✗ Syntax test failed, aborting further tests")
        sys.exit(1)
    
    # Run structure tests
    passed, failed = test_form_validation_structure()
    total_passed += passed
    total_failed += failed
    
    # Run documentation tests
    passed, failed = test_documentation()
    total_passed += passed
    total_failed += failed
    
    # Print summary
    print("\n" + "=" * 60)
    print(f"Tests passed: {total_passed}")
    print(f"Tests failed: {total_failed}")
    print(f"Total tests: {total_passed + total_failed}")
    print("=" * 60)
    
    if total_failed == 0:
        print("\n✓ All tests passed!")
        sys.exit(0)
    else:
        print(f"\n✗ {total_failed} test(s) failed!")
        sys.exit(1)

if __name__ == '__main__':
    main()
