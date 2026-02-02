# Lazy Loading Integration Test

## Overview

This integration test validates the lazy loading behavior for images in the DashBoard application.

**Feature**: frontend-ui-optimization  
**Property 7**: Image lazy loading behavior  
**Validates**: Requirements 9.3

## Test Objectives

The integration test verifies that:

1. ✅ Images outside viewport should not be loaded initially
2. ✅ Images should load when scrolled into viewport
3. ✅ Images should have proper loading states (`is-loading`, `is-loaded`)
4. ✅ IntersectionObserver API is used when supported
5. ✅ Multiple images load sequentially as they enter viewport

## Files

- `lazy-loading.js` - The lazy loading module implementation
- `lazy-loading-integration.test.js` - Integration test suite
- `lazy-loading-integration-test.html` - HTML test runner
- `lazy-loading.test.js` - Unit tests (existing)
- `lazy-loading-test.html` - Manual test page (existing)

## Running the Integration Test

### Method 1: Browser-Based Test (Recommended)

1. Start the Django development server:
   ```bash
   python manage.py runserver
   ```

2. Open the test page in your browser:
   ```
   http://localhost:8000/static/js/lazy-loading-integration-test.html
   ```

3. Click the "▶️ Run Integration Tests" button

4. The test will automatically:
   - Scroll through the page
   - Check image loading behavior
   - Display a detailed test report

### Method 2: Direct File Access

1. Navigate to the test file:
   ```bash
   cd main/static/js
   ```

2. Open `lazy-loading-integration-test.html` directly in your browser

3. Click "▶️ Run Integration Tests"

## Test Results

The test will display:

- ✅ **Passed tests**: Green background with checkmark
- ❌ **Failed tests**: Red background with X mark
- **Summary**: Total passed/failed count
- **Details**: Specific messages for each test

## Expected Behavior

### Images Above the Fold
- Should load immediately when page loads
- Should have `is-loaded` class applied

### Images Below the Fold
- Should NOT load initially
- Should have `is-loading` class initially
- Should load when scrolled into viewport (within 50px margin)
- Should transition from `is-loading` to `is-loaded` class

## Browser Compatibility

The test checks for IntersectionObserver support:

- ✅ **Modern browsers**: Uses IntersectionObserver for efficient lazy loading
- ⚠️ **Older browsers**: Falls back to loading all images immediately

Supported browsers:
- Chrome 51+
- Firefox 55+
- Safari 12.1+
- Edge 15+

## Debugging

### Console Output

The test logs detailed information to the browser console:

```javascript
🧪 Running Lazy Loading Integration Tests...
Feature: frontend-ui-optimization
Property 7: Image lazy loading behavior
Validates: Requirements 9.3

✅ Test 1: Images outside viewport should not load initially PASSED
✅ Test 2: Images should have loading class initially PASSED
✅ Test 3: Images should load when scrolled into viewport PASSED
...
```

### Common Issues

**Issue**: Images load immediately even when below the fold
- **Cause**: Browser native lazy loading may be active
- **Solution**: The test accounts for this and checks the LazyLoader behavior

**Issue**: Tests timeout
- **Cause**: Slow network or large images
- **Solution**: Tests have 3-5 second timeouts; check network speed

**Issue**: IntersectionObserver not supported
- **Cause**: Old browser version
- **Solution**: Test will pass but note the fallback mode is used

## Integration with Django

To use the lazy loading module in Django templates:

```html
{% load static %}

<!-- Include the lazy loading module -->
<script src="{% static 'js/lazy-loading.js' %}"></script>

<!-- Use lazy loading on images -->
<img 
    src="{% static 'Images/placeholder.jpg' %}" 
    data-src="{% static 'Images/dish-1.jpg' %}"
    loading="lazy" 
    alt="Dish name"
    width="400"
    height="300"
>

<!-- Initialize the lazy loader -->
<script>
    const lazyLoader = new LazyLoader({
        rootMargin: '50px',
        threshold: 0.01
    });
    lazyLoader.init();
</script>
```

## Performance Benefits

Lazy loading provides:

- 📉 **Reduced initial page load**: Only loads visible images
- 🚀 **Faster Time to Interactive**: Less data to download initially
- 💾 **Bandwidth savings**: Users don't download images they never see
- 📱 **Better mobile experience**: Especially important on slow connections

## Maintenance

When updating the lazy loading module:

1. Run the integration tests to ensure behavior is preserved
2. Update tests if new features are added
3. Check that all 6 tests pass before deploying

## Related Tests

- **Unit Tests**: `lazy-loading.test.js` - Tests individual methods
- **Manual Test**: `lazy-loading-test.html` - Visual verification
- **Integration Test**: `lazy-loading-integration.test.js` - End-to-end behavior

## Requirements Validation

This test validates **Requirement 9.3** from the design document:

> WHEN images are displayed below the fold, THE Page SHALL implement lazy loading to defer loading until needed

The integration test ensures this requirement is met by:
1. Verifying images below fold don't load initially
2. Verifying images load when entering viewport
3. Verifying proper state management during loading
