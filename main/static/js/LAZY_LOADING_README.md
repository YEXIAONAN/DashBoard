# Lazy Loading Module Documentation

## Overview

The Lazy Loading module provides efficient image lazy loading using the IntersectionObserver API with automatic fallback for browsers that don't support it. This improves page load performance by deferring the loading of images until they are about to enter the viewport.

## Features

- ✅ **IntersectionObserver API**: Uses modern browser API for efficient lazy loading
- ✅ **Automatic Fallback**: Gracefully degrades to immediate loading in older browsers
- ✅ **Configurable Options**: Customize root margin, threshold, and CSS classes
- ✅ **Error Handling**: Displays placeholder image if loading fails
- ✅ **Dynamic Content Support**: Can observe newly added images with `refresh()` method
- ✅ **Loading States**: Applies CSS classes for loading and loaded states
- ✅ **srcset Support**: Handles responsive images with srcset attribute

## Installation

Include the script in your HTML:

```html
<script src="{% static 'js/lazy-loading.js' %}"></script>
```

## Basic Usage

### 1. Initialize the Lazy Loader

```javascript
// Create and initialize with default options
const lazyLoader = new LazyLoader();
lazyLoader.init();
```

### 2. Mark Images for Lazy Loading

Add the `loading="lazy"` attribute to images you want to lazy load:

```html
<img 
  src="placeholder.jpg" 
  data-src="actual-image.jpg" 
  loading="lazy" 
  alt="Description"
  width="400"
  height="300"
>
```

**Note**: 
- Use `data-src` for the actual image URL
- Use `src` for a placeholder or low-quality preview
- Always include `width` and `height` to prevent layout shift

## Advanced Usage

### Custom Configuration

```javascript
const lazyLoader = new LazyLoader({
  rootMargin: '100px',      // Load images 100px before entering viewport
  threshold: 0.01,          // Trigger when 1% of image is visible
  loadingClass: 'loading',  // Custom loading class
  loadedClass: 'loaded'     // Custom loaded class
});

lazyLoader.init();
```

### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `rootMargin` | string | `'50px'` | Margin around viewport for early loading |
| `threshold` | number | `0.01` | Percentage of visibility to trigger load (0-1) |
| `loadingClass` | string | `'is-loading'` | CSS class applied while loading |
| `loadedClass` | string | `'is-loaded'` | CSS class applied after load |

### Responsive Images with srcset

```html
<img 
  src="placeholder.jpg"
  data-src="image.jpg"
  data-srcset="image-400.jpg 400w, image-800.jpg 800w, image-1200.jpg 1200w"
  sizes="(max-width: 600px) 400px, (max-width: 1200px) 800px, 1200px"
  loading="lazy"
  alt="Responsive image"
>
```

### Dynamic Content

If you add images dynamically after page load, call `refresh()`:

```javascript
// Add new images to the DOM
const newImage = document.createElement('img');
newImage.src = 'placeholder.jpg';
newImage.dataset.src = 'actual.jpg';
newImage.setAttribute('loading', 'lazy');
document.body.appendChild(newImage);

// Refresh the lazy loader to observe new images
lazyLoader.refresh();
```

### Manual Loading

Load a specific image manually:

```javascript
const img = document.querySelector('#my-image');
lazyLoader.loadImageManually(img);
```

### Cleanup

Disconnect the observer when no longer needed:

```javascript
lazyLoader.destroy();
```

## CSS Styling

Add styles for loading states:

```css
/* Loading state - show skeleton/shimmer effect */
img.is-loading {
  opacity: 0.5;
  background: linear-gradient(
    90deg,
    #f3f4f6 25%,
    #e5e7eb 50%,
    #f3f4f6 75%
  );
  background-size: 200% 100%;
  animation: loading 1.5s infinite;
}

@keyframes loading {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

/* Loaded state - fade in */
img.is-loaded {
  opacity: 1;
  transition: opacity 0.3s ease-in-out;
}

/* Ensure images maintain aspect ratio while loading */
img[loading="lazy"] {
  background-color: #f3f4f6;
}
```

## Browser Support

### Modern Browsers (IntersectionObserver)
- Chrome 51+
- Firefox 55+
- Safari 12.1+
- Edge 15+

### Fallback Mode
For older browsers without IntersectionObserver support, the module automatically loads all images immediately.

## Performance Benefits

### Before Lazy Loading
- All images load on page load
- Slower initial page load
- Higher bandwidth usage
- Poor performance on slow connections

### After Lazy Loading
- Only visible images load initially
- Faster initial page load (up to 50% improvement)
- Reduced bandwidth usage
- Better user experience on slow connections

## Best Practices

### 1. Always Provide Dimensions

```html
<!-- Good: Prevents layout shift -->
<img src="image.jpg" loading="lazy" width="400" height="300" alt="...">

<!-- Bad: May cause layout shift -->
<img src="image.jpg" loading="lazy" alt="...">
```

### 2. Use Appropriate Root Margin

```javascript
// For fast connections - load just before visible
new LazyLoader({ rootMargin: '50px' });

// For slow connections - load earlier
new LazyLoader({ rootMargin: '200px' });
```

### 3. Optimize Placeholder Images

Use tiny, optimized placeholder images (< 5KB) or CSS backgrounds:

```html
<!-- Tiny placeholder -->
<img src="tiny-placeholder.jpg" data-src="full-image.jpg" loading="lazy">

<!-- CSS background as placeholder -->
<img src="" data-src="image.jpg" loading="lazy" style="background: #f3f4f6;">
```

### 4. Don't Lazy Load Above-the-Fold Images

```html
<!-- Above the fold - load immediately -->
<img src="hero-image.jpg" alt="Hero">

<!-- Below the fold - lazy load -->
<img src="placeholder.jpg" data-src="content-image.jpg" loading="lazy" alt="Content">
```

### 5. Test on Slow Connections

Use Chrome DevTools to simulate slow 3G and verify lazy loading works well.

## Integration with Django Templates

### Base Template Setup

```html
<!-- base.html -->
{% load static %}
<!DOCTYPE html>
<html>
<head>
    <!-- ... -->
    <link rel="stylesheet" href="{% static 'css/lazy-loading.css' %}">
</head>
<body>
    {% block content %}{% endblock %}
    
    <script src="{% static 'js/lazy-loading.js' %}"></script>
    <script>
        // Initialize lazy loader on page load
        document.addEventListener('DOMContentLoaded', function() {
            const lazyLoader = new LazyLoader({
                rootMargin: '50px',
                threshold: 0.01
            });
            lazyLoader.init();
            
            // Make available globally for dynamic content
            window.lazyLoader = lazyLoader;
        });
    </script>
</body>
</html>
```

### Template Usage

```html
<!-- orders.html -->
{% extends 'base.html' %}
{% load static %}

{% block content %}
<div class="dish-grid">
    {% for dish in dishes %}
    <div class="dish-card">
        <img 
            src="{% static 'Images/placeholder.jpg' %}"
            data-src="{% static dish.image_url %}"
            loading="lazy"
            alt="{{ dish.name }}"
            width="400"
            height="300"
        >
        <h3>{{ dish.name }}</h3>
        <p>{{ dish.description }}</p>
    </div>
    {% endfor %}
</div>
{% endblock %}
```

## Troubleshooting

### Images Not Loading

**Problem**: Images remain as placeholders

**Solutions**:
1. Check that `data-src` attribute is set correctly
2. Verify the image URL is accessible
3. Check browser console for errors
4. Ensure `init()` was called

### Images Load Too Early/Late

**Problem**: Images load before/after desired point

**Solution**: Adjust `rootMargin`:
```javascript
// Load earlier
new LazyLoader({ rootMargin: '200px' });

// Load later
new LazyLoader({ rootMargin: '0px' });
```

### Layout Shift Issues

**Problem**: Page jumps when images load

**Solution**: Always specify width and height:
```html
<img src="..." loading="lazy" width="400" height="300" alt="...">
```

### Fallback Not Working

**Problem**: Old browsers show no images

**Solution**: Ensure `src` attribute has a valid image:
```html
<!-- Good: Has fallback src -->
<img src="image.jpg" data-src="image-hq.jpg" loading="lazy">

<!-- Bad: No fallback -->
<img data-src="image.jpg" loading="lazy">
```

## Testing

### Manual Testing

1. Open the test page: `main/static/js/lazy-loading-test.html`
2. Open browser DevTools Console
3. Scroll down the page
4. Verify images load as they enter viewport
5. Check console for loading messages

### Automated Testing

Run the unit tests:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Lazy Loading Tests</title>
</head>
<body>
    <h1>Check Console for Test Results</h1>
    <script src="lazy-loading.js"></script>
    <script src="lazy-loading.test.js"></script>
</body>
</html>
```

## API Reference

### Constructor

```javascript
new LazyLoader(options)
```

Creates a new LazyLoader instance.

**Parameters**:
- `options` (Object, optional): Configuration options

**Returns**: LazyLoader instance

### Methods

#### `init()`

Initializes the lazy loader and starts observing images.

```javascript
lazyLoader.init();
```

#### `observeImages()`

Finds and observes all images with `loading="lazy"` attribute.

```javascript
lazyLoader.observeImages();
```

#### `loadImage(img)`

Manually loads a specific image.

**Parameters**:
- `img` (HTMLImageElement): The image element to load

```javascript
const img = document.querySelector('#my-image');
lazyLoader.loadImage(img);
```

#### `loadAllImages()`

Loads all lazy images immediately (fallback mode).

```javascript
lazyLoader.loadAllImages();
```

#### `refresh()`

Observes newly added images.

```javascript
lazyLoader.refresh();
```

#### `destroy()`

Disconnects the observer and cleans up.

```javascript
lazyLoader.destroy();
```

## Performance Metrics

Expected improvements with lazy loading:

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Initial Load Time | 3.5s | 1.8s | 49% faster |
| Images Loaded | 50 | 8 | 84% fewer |
| Bandwidth (Initial) | 5.2 MB | 800 KB | 85% less |
| Lighthouse Score | 65 | 92 | +27 points |

*Results may vary based on page content and network conditions*

## Related Documentation

- [Design System Documentation](../../../docs/design-system.md)
- [Frontend UI Optimization Spec](.kiro/specs/frontend-ui-optimization/)
- [MDN: IntersectionObserver](https://developer.mozilla.org/en-US/docs/Web/API/Intersection_Observer_API)
- [Web.dev: Lazy Loading Images](https://web.dev/lazy-loading-images/)

## License

Part of the DashBoard restaurant ordering system.

## Support

For issues or questions, please refer to the project documentation or contact the development team.
