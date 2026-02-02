# Design Document: Frontend UI Optimization

## Overview

This design document outlines the systematic optimization of the DashBoard restaurant ordering system's frontend user interface. The optimization establishes a unified design system, improves responsiveness, enhances user interactions, and optimizes performance across all seven pages while maintaining existing Django-based functionality.

### Goals

1. Create a cohesive design system with standardized components, colors, and typography
2. Implement responsive layouts that work seamlessly across desktop, tablet, and mobile devices
3. Enhance user experience with smooth animations, clear feedback, and intuitive interactions
4. Optimize performance through image compression, lazy loading, and code minification
5. Ensure accessibility compliance (WCAG 2.1 AA) and cross-browser compatibility
6. Improve SEO with proper metadata and semantic HTML
7. Maintain all existing functionality while improving visual design

### Scope

The optimization covers seven Django template pages:
- `index.html` - Home page with personalized recommendations
- `orders.html` - Dish browsing and ordering interface
- `profile.html` - User profile and settings
- `repo.html` - Nutrition reports and analytics
- `order_history.html` - Past order history
- `ai_health_advisor.html` - AI chat interface
- `login.html` - Authentication page

### Constraints

- Must work within Django template engine (no React/Vue migration)
- Must preserve existing backend API contracts
- Must maintain session-based authentication flow
- Must support existing MySQL database schema
- Must not break robotic arm integration or YOLO vision features
- Should minimize external dependencies to reduce bundle size

## Architecture

### High-Level Architecture

The frontend architecture follows Django's MVT (Model-View-Template) pattern with enhanced static asset organization:

```
┌─────────────────────────────────────────────────────────────┐
│                        Browser Layer                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   HTML/CSS   │  │  JavaScript  │  │    Images    │      │
│  │  (Templates) │  │   (Vanilla)  │  │   (WebP/JP)  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            ↕
┌─────────────────────────────────────────────────────────────┐
│                    Django Static Files                       │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  main/static/                                        │   │
│  │  ├── css/                                            │   │
│  │  │   ├── design-system.css  (Design tokens)         │   │
│  │  │   ├── components.css     (Reusable components)   │   │
│  │  │   ├── layouts.css        (Grid/Flexbox layouts)  │   │
│  │  │   ├── animations.css     (Transitions/effects)   │   │
│  │  │   └── pages/             (Page-specific styles)  │   │
│  │  ├── js/                                             │   │
│  │  │   ├── design-system.js   (Component behaviors)   │   │
│  │  │   ├── form-validation.js (Real-time validation)  │   │
│  │  │   ├── lazy-loading.js    (Image optimization)    │   │
│  │  │   └── animations.js      (Interaction effects)   │   │
│  │  └── Images/                                         │   │
│  │      ├── optimized/         (WebP + JPEG fallback)  │   │
│  │      └── sprites/           (Icon sprites)          │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            ↕
┌─────────────────────────────────────────────────────────────┐
│                    Django Template Layer                     │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  main/templates/                                     │   │
│  │  ├── base.html              (Base template)         │   │
│  │  ├── components/            (Reusable components)   │   │
│  │  │   ├── navbar.html                                │   │
│  │  │   ├── card.html                                  │   │
│  │  │   ├── button.html                                │   │
│  │  │   └── form-field.html                            │   │
│  │  └── pages/                 (Page templates)        │   │
│  │      ├── index.html                                 │   │
│  │      ├── orders.html                                │   │
│  │      └── ...                                        │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            ↕
┌─────────────────────────────────────────────────────────────┐
│                    Django Views Layer                        │
│              (main/views.py - No changes needed)             │
└─────────────────────────────────────────────────────────────┘
```

### Design System Architecture

The design system is implemented as a layered CSS architecture:

**Layer 1: Design Tokens** (`design-system.css`)
- CSS custom properties for colors, typography, spacing, shadows
- Provides single source of truth for all visual values
- Enables theme switching and easy maintenance

**Layer 2: Component Styles** (`components.css`)
- Reusable component classes (buttons, cards, forms, navigation)
- Built using design tokens from Layer 1
- BEM naming convention for clarity

**Layer 3: Layout Utilities** (`layouts.css`)
- Grid and Flexbox utilities for responsive layouts
- Breakpoint-specific classes
- Spacing utilities

**Layer 4: Page-Specific Styles** (`pages/*.css`)
- Unique styles for individual pages
- Minimal custom CSS (most styling from Layers 1-3)
- Page-specific overrides only when necessary



## Components and Interfaces

### Design System Components

#### 1. Design Tokens (CSS Custom Properties)

**Color System:**
```css
:root {
  /* Primary Brand Colors */
  --color-primary: #10b981;      /* Green - primary actions */
  --color-primary-light: #34d399; /* Light green - hover states */
  --color-primary-dark: #059669;  /* Dark green - active states */
  
  /* Secondary Colors */
  --color-secondary: #ffffff;     /* White - backgrounds */
  --color-secondary-dark: #f9fafb; /* Light gray - alternate backgrounds */
  
  /* Accent Color */
  --color-accent: #3b82f6;        /* Blue - links and info */
  
  /* Semantic Colors */
  --color-success: #10b981;       /* Success messages */
  --color-error: #ef4444;         /* Error messages */
  --color-warning: #f59e0b;       /* Warning messages */
  --color-info: #3b82f6;          /* Info messages */
  
  /* Neutral Colors */
  --color-text-primary: #111827;   /* Primary text */
  --color-text-secondary: #6b7280; /* Secondary text */
  --color-text-disabled: #9ca3af;  /* Disabled text */
  --color-border: #e5e7eb;         /* Borders */
  --color-background: #ffffff;     /* Main background */
  --color-surface: #f9fafb;        /* Card/surface background */
}
```

**Typography System:**
```css
:root {
  /* Font Families */
  --font-primary: 'Roboto', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  --font-secondary: 'Open Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  --font-monospace: 'Courier New', monospace;
  
  /* Font Sizes */
  --font-size-xs: 0.75rem;    /* 12px */
  --font-size-sm: 0.875rem;   /* 14px */
  --font-size-base: 1rem;     /* 16px */
  --font-size-lg: 1.125rem;   /* 18px */
  --font-size-xl: 1.25rem;    /* 20px */
  --font-size-2xl: 1.5rem;    /* 24px */
  --font-size-3xl: 2rem;      /* 32px */
  
  /* Font Weights */
  --font-weight-normal: 400;
  --font-weight-medium: 500;
  --font-weight-semibold: 600;
  --font-weight-bold: 700;
  
  /* Line Heights */
  --line-height-tight: 1.25;
  --line-height-normal: 1.5;
  --line-height-relaxed: 1.75;
}
```

**Spacing System (8px base grid):**
```css
:root {
  --spacing-0: 0;
  --spacing-1: 0.25rem;  /* 4px */
  --spacing-2: 0.5rem;   /* 8px */
  --spacing-3: 0.75rem;  /* 12px */
  --spacing-4: 1rem;     /* 16px */
  --spacing-5: 1.25rem;  /* 20px */
  --spacing-6: 1.5rem;   /* 24px */
  --spacing-8: 2rem;     /* 32px */
  --spacing-10: 2.5rem;  /* 40px */
  --spacing-12: 3rem;    /* 48px */
  --spacing-16: 4rem;    /* 64px */
}
```

**Shadow System:**
```css
:root {
  --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  --shadow-base: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
  --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
}
```

**Border Radius:**
```css
:root {
  --radius-sm: 0.25rem;   /* 4px */
  --radius-base: 0.5rem;  /* 8px */
  --radius-md: 0.75rem;   /* 12px */
  --radius-lg: 1rem;      /* 16px */
  --radius-full: 9999px;  /* Fully rounded */
}
```

**Transitions:**
```css
:root {
  --transition-fast: 150ms ease-in-out;
  --transition-base: 250ms ease-in-out;
  --transition-slow: 400ms ease-in-out;
}
```

#### 2. Button Component

**HTML Structure:**
```html
<button class="btn btn--primary btn--md">
  <span class="btn__text">Submit Order</span>
</button>
```

**CSS Implementation:**
```css
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-family: var(--font-primary);
  font-weight: var(--font-weight-medium);
  border: none;
  border-radius: var(--radius-base);
  cursor: pointer;
  transition: all var(--transition-base);
  text-decoration: none;
}

.btn:focus {
  outline: 2px solid var(--color-primary);
  outline-offset: 2px;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Variants */
.btn--primary {
  background-color: var(--color-primary);
  color: white;
}

.btn--primary:hover:not(:disabled) {
  background-color: var(--color-primary-dark);
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

.btn--secondary {
  background-color: var(--color-surface);
  color: var(--color-text-primary);
  border: 1px solid var(--color-border);
}

.btn--secondary:hover:not(:disabled) {
  background-color: var(--color-secondary-dark);
}

/* Sizes */
.btn--sm {
  padding: var(--spacing-2) var(--spacing-4);
  font-size: var(--font-size-sm);
}

.btn--md {
  padding: var(--spacing-3) var(--spacing-6);
  font-size: var(--font-size-base);
}

.btn--lg {
  padding: var(--spacing-4) var(--spacing-8);
  font-size: var(--font-size-lg);
}
```

#### 3. Card Component

**HTML Structure:**
```html
<div class="card">
  <div class="card__image">
    <img src="dish.webp" alt="Dish name" loading="lazy">
  </div>
  <div class="card__content">
    <h3 class="card__title">Dish Name</h3>
    <p class="card__description">Description text</p>
  </div>
  <div class="card__actions">
    <button class="btn btn--primary btn--sm">Add to Order</button>
  </div>
</div>
```

**CSS Implementation:**
```css
.card {
  background-color: var(--color-background);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-base);
  overflow: hidden;
  transition: all var(--transition-base);
}

.card:hover {
  box-shadow: var(--shadow-lg);
  transform: translateY(-2px);
}

.card__image {
  width: 100%;
  aspect-ratio: 16 / 9;
  overflow: hidden;
}

.card__image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform var(--transition-slow);
}

.card:hover .card__image img {
  transform: scale(1.05);
}

.card__content {
  padding: var(--spacing-4);
}

.card__title {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin-bottom: var(--spacing-2);
}

.card__description {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  line-height: var(--line-height-normal);
}

.card__actions {
  padding: var(--spacing-4);
  border-top: 1px solid var(--color-border);
  display: flex;
  justify-content: flex-end;
  gap: var(--spacing-2);
}
```

#### 4. Form Field Component

**HTML Structure:**
```html
<div class="form-field">
  <label class="form-field__label" for="email">Email Address</label>
  <input 
    type="email" 
    id="email" 
    class="form-field__input" 
    placeholder="you@example.com"
    aria-describedby="email-error"
  >
  <span class="form-field__error" id="email-error" role="alert"></span>
  <span class="form-field__helper">We'll never share your email</span>
</div>
```

**CSS Implementation:**
```css
.form-field {
  margin-bottom: var(--spacing-4);
}

.form-field__label {
  display: block;
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
  margin-bottom: var(--spacing-2);
}

.form-field__input {
  width: 100%;
  padding: var(--spacing-3) var(--spacing-4);
  font-size: var(--font-size-base);
  font-family: var(--font-primary);
  color: var(--color-text-primary);
  background-color: var(--color-background);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-base);
  transition: all var(--transition-fast);
}

.form-field__input:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.1);
}

.form-field__input.is-invalid {
  border-color: var(--color-error);
}

.form-field__input.is-valid {
  border-color: var(--color-success);
}

.form-field__error {
  display: none;
  font-size: var(--font-size-sm);
  color: var(--color-error);
  margin-top: var(--spacing-2);
}

.form-field__input.is-invalid ~ .form-field__error {
  display: block;
}

.form-field__helper {
  display: block;
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
  margin-top: var(--spacing-2);
}
```

#### 5. Navigation Bar Component

**HTML Structure:**
```html
<nav class="navbar">
  <div class="navbar__container">
    <a href="/" class="navbar__brand">
      <img src="logo.svg" alt="DashBoard" class="navbar__logo">
    </a>
    
    <button class="navbar__toggle" aria-label="Toggle navigation">
      <span class="navbar__toggle-icon"></span>
    </button>
    
    <ul class="navbar__menu">
      <li class="navbar__item">
        <a href="/" class="navbar__link navbar__link--active">Home</a>
      </li>
      <li class="navbar__item">
        <a href="/orders" class="navbar__link">Orders</a>
      </li>
      <li class="navbar__item">
        <a href="/profile" class="navbar__link">Profile</a>
      </li>
      <li class="navbar__item">
        <a href="/repo" class="navbar__link">Reports</a>
      </li>
      <li class="navbar__item">
        <a href="/order_history" class="navbar__link">History</a>
      </li>
      <li class="navbar__item">
        <a href="/ai_health_advisor" class="navbar__link">AI Advisor</a>
      </li>
    </ul>
  </div>
</nav>
```

**CSS Implementation:**
```css
.navbar {
  background-color: var(--color-background);
  box-shadow: var(--shadow-sm);
  position: sticky;
  top: 0;
  z-index: 1000;
}

.navbar__container {
  max-width: 1280px;
  margin: 0 auto;
  padding: var(--spacing-4) var(--spacing-6);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.navbar__brand {
  display: flex;
  align-items: center;
  text-decoration: none;
}

.navbar__logo {
  height: 40px;
  width: auto;
}

.navbar__toggle {
  display: none;
  background: none;
  border: none;
  cursor: pointer;
  padding: var(--spacing-2);
}

.navbar__menu {
  display: flex;
  list-style: none;
  margin: 0;
  padding: 0;
  gap: var(--spacing-2);
}

.navbar__link {
  display: block;
  padding: var(--spacing-2) var(--spacing-4);
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-secondary);
  text-decoration: none;
  border-radius: var(--radius-base);
  transition: all var(--transition-fast);
}

.navbar__link:hover {
  color: var(--color-primary);
  background-color: var(--color-surface);
}

.navbar__link--active {
  color: var(--color-primary);
  background-color: rgba(16, 185, 129, 0.1);
}

/* Mobile Responsive */
@media (max-width: 768px) {
  .navbar__toggle {
    display: block;
  }
  
  .navbar__menu {
    position: absolute;
    top: 100%;
    left: 0;
    right: 0;
    background-color: var(--color-background);
    flex-direction: column;
    box-shadow: var(--shadow-lg);
    max-height: 0;
    overflow: hidden;
    transition: max-height var(--transition-base);
  }
  
  .navbar__menu.is-open {
    max-height: 500px;
  }
  
  .navbar__item {
    border-bottom: 1px solid var(--color-border);
  }
  
  .navbar__link {
    padding: var(--spacing-4) var(--spacing-6);
  }
}
```

#### 6. Loading Indicator Component

**HTML Structure:**
```html
<div class="loading-indicator">
  <div class="loading-indicator__spinner"></div>
  <p class="loading-indicator__text">Loading...</p>
</div>
```

**CSS Implementation:**
```css
.loading-indicator {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-8);
}

.loading-indicator__spinner {
  width: 40px;
  height: 40px;
  border: 4px solid var(--color-surface);
  border-top-color: var(--color-primary);
  border-radius: var(--radius-full);
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-indicator__text {
  margin-top: var(--spacing-4);
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}
```

#### 7. Toast Notification Component

**HTML Structure:**
```html
<div class="toast toast--success" role="alert">
  <div class="toast__icon">✓</div>
  <div class="toast__content">
    <p class="toast__title">Success</p>
    <p class="toast__message">Order submitted successfully</p>
  </div>
  <button class="toast__close" aria-label="Close">&times;</button>
</div>
```

**CSS Implementation:**
```css
.toast {
  position: fixed;
  top: var(--spacing-6);
  right: var(--spacing-6);
  min-width: 300px;
  max-width: 400px;
  background-color: var(--color-background);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-xl);
  display: flex;
  align-items: flex-start;
  padding: var(--spacing-4);
  gap: var(--spacing-3);
  animation: slideIn 0.3s ease-out;
  z-index: 2000;
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

.toast__icon {
  width: 24px;
  height: 24px;
  border-radius: var(--radius-full);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: var(--font-weight-bold);
  flex-shrink: 0;
}

.toast--success .toast__icon {
  background-color: var(--color-success);
  color: white;
}

.toast--error .toast__icon {
  background-color: var(--color-error);
  color: white;
}

.toast__content {
  flex: 1;
}

.toast__title {
  font-weight: var(--font-weight-semibold);
  font-size: var(--font-size-base);
  color: var(--color-text-primary);
  margin-bottom: var(--spacing-1);
}

.toast__message {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.toast__close {
  background: none;
  border: none;
  font-size: var(--font-size-2xl);
  color: var(--color-text-secondary);
  cursor: pointer;
  padding: 0;
  line-height: 1;
  transition: color var(--transition-fast);
}

.toast__close:hover {
  color: var(--color-text-primary);
}
```

### JavaScript Interfaces

#### Form Validation Module

**Interface:**
```javascript
// form-validation.js
class FormValidator {
  constructor(formElement, rules) {
    this.form = formElement;
    this.rules = rules;
    this.errors = {};
  }
  
  // Validate a single field
  validateField(fieldName, value) {
    const rule = this.rules[fieldName];
    if (!rule) return true;
    
    if (rule.required && !value) {
      return { valid: false, message: `${fieldName} is required` };
    }
    
    if (rule.pattern && !rule.pattern.test(value)) {
      return { valid: false, message: rule.message };
    }
    
    if (rule.minLength && value.length < rule.minLength) {
      return { valid: false, message: `Minimum ${rule.minLength} characters` };
    }
    
    return { valid: true };
  }
  
  // Validate entire form
  validateForm() {
    const formData = new FormData(this.form);
    let isValid = true;
    
    for (const [fieldName, value] of formData.entries()) {
      const result = this.validateField(fieldName, value);
      if (!result.valid) {
        this.errors[fieldName] = result.message;
        isValid = false;
      }
    }
    
    return isValid;
  }
  
  // Display error for a field
  showError(fieldName, message) {
    const field = this.form.querySelector(`[name="${fieldName}"]`);
    const errorElement = field.parentElement.querySelector('.form-field__error');
    
    field.classList.add('is-invalid');
    field.classList.remove('is-valid');
    if (errorElement) {
      errorElement.textContent = message;
    }
  }
  
  // Clear error for a field
  clearError(fieldName) {
    const field = this.form.querySelector(`[name="${fieldName}"]`);
    const errorElement = field.parentElement.querySelector('.form-field__error');
    
    field.classList.remove('is-invalid');
    field.classList.add('is-valid');
    if (errorElement) {
      errorElement.textContent = '';
    }
  }
  
  // Initialize real-time validation
  init() {
    const fields = this.form.querySelectorAll('input, textarea, select');
    
    fields.forEach(field => {
      field.addEventListener('blur', (e) => {
        const result = this.validateField(e.target.name, e.target.value);
        if (!result.valid) {
          this.showError(e.target.name, result.message);
        } else {
          this.clearError(e.target.name);
        }
      });
    });
    
    this.form.addEventListener('submit', (e) => {
      e.preventDefault();
      if (this.validateForm()) {
        this.form.submit();
      } else {
        // Show all errors
        for (const [fieldName, message] of Object.entries(this.errors)) {
          this.showError(fieldName, message);
        }
      }
    });
  }
}
```

#### Lazy Loading Module

**Interface:**
```javascript
// lazy-loading.js
class LazyLoader {
  constructor(options = {}) {
    this.options = {
      rootMargin: options.rootMargin || '50px',
      threshold: options.threshold || 0.01,
      loadingClass: options.loadingClass || 'is-loading',
      loadedClass: options.loadedClass || 'is-loaded'
    };
    
    this.observer = null;
  }
  
  // Initialize Intersection Observer
  init() {
    if ('IntersectionObserver' in window) {
      this.observer = new IntersectionObserver(
        this.handleIntersection.bind(this),
        {
          rootMargin: this.options.rootMargin,
          threshold: this.options.threshold
        }
      );
      
      this.observeImages();
    } else {
      // Fallback: load all images immediately
      this.loadAllImages();
    }
  }
  
  // Observe all lazy images
  observeImages() {
    const images = document.querySelectorAll('img[loading="lazy"]');
    images.forEach(img => {
      img.classList.add(this.options.loadingClass);
      this.observer.observe(img);
    });
  }
  
  // Handle intersection
  handleIntersection(entries) {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        this.loadImage(entry.target);
        this.observer.unobserve(entry.target);
      }
    });
  }
  
  // Load a single image
  loadImage(img) {
    const src = img.dataset.src || img.src;
    const srcset = img.dataset.srcset;
    
    img.src = src;
    if (srcset) {
      img.srcset = srcset;
    }
    
    img.addEventListener('load', () => {
      img.classList.remove(this.options.loadingClass);
      img.classList.add(this.options.loadedClass);
    });
  }
  
  // Fallback: load all images
  loadAllImages() {
    const images = document.querySelectorAll('img[loading="lazy"]');
    images.forEach(img => this.loadImage(img));
  }
}
```

#### Toast Notification Module

**Interface:**
```javascript
// toast.js
class ToastManager {
  constructor() {
    this.container = this.createContainer();
    this.toasts = [];
  }
  
  // Create toast container
  createContainer() {
    let container = document.querySelector('.toast-container');
    if (!container) {
      container = document.createElement('div');
      container.className = 'toast-container';
      document.body.appendChild(container);
    }
    return container;
  }
  
  // Show toast notification
  show(message, type = 'success', duration = 5000) {
    const toast = this.createToast(message, type);
    this.container.appendChild(toast);
    this.toasts.push(toast);
    
    // Auto-dismiss after duration
    setTimeout(() => {
      this.dismiss(toast);
    }, duration);
    
    return toast;
  }
  
  // Create toast element
  createToast(message, type) {
    const toast = document.createElement('div');
    toast.className = `toast toast--${type}`;
    toast.setAttribute('role', 'alert');
    
    const icon = type === 'success' ? '✓' : '✕';
    const title = type.charAt(0).toUpperCase() + type.slice(1);
    
    toast.innerHTML = `
      <div class="toast__icon">${icon}</div>
      <div class="toast__content">
        <p class="toast__title">${title}</p>
        <p class="toast__message">${message}</p>
      </div>
      <button class="toast__close" aria-label="Close">&times;</button>
    `;
    
    // Close button handler
    toast.querySelector('.toast__close').addEventListener('click', () => {
      this.dismiss(toast);
    });
    
    return toast;
  }
  
  // Dismiss toast
  dismiss(toast) {
    toast.style.animation = 'slideOut 0.3s ease-out';
    setTimeout(() => {
      toast.remove();
      this.toasts = this.toasts.filter(t => t !== toast);
    }, 300);
  }
}

// Global toast instance
window.toast = new ToastManager();
```



## Data Models

### CSS Class Naming Convention (BEM)

The design system uses BEM (Block Element Modifier) naming convention for CSS classes:

**Structure:**
```
.block { }                  /* Component */
.block__element { }         /* Child element */
.block--modifier { }        /* Variant */
.block__element--modifier { } /* Element variant */
```

**Examples:**
```css
.card { }                   /* Block */
.card__image { }            /* Element */
.card__title { }            /* Element */
.card--featured { }         /* Modifier */
.card__image--rounded { }   /* Element modifier */
```

### Responsive Breakpoints

**Breakpoint System:**
```css
/* Mobile First Approach */
:root {
  --breakpoint-sm: 640px;   /* Small devices */
  --breakpoint-md: 768px;   /* Medium devices (tablets) */
  --breakpoint-lg: 1024px;  /* Large devices (desktops) */
  --breakpoint-xl: 1280px;  /* Extra large devices */
}
```

**Media Query Usage:**
```css
/* Mobile (default) */
.container {
  padding: var(--spacing-4);
}

/* Tablet and up */
@media (min-width: 768px) {
  .container {
    padding: var(--spacing-6);
  }
}

/* Desktop and up */
@media (min-width: 1024px) {
  .container {
    padding: var(--spacing-8);
    max-width: 1280px;
    margin: 0 auto;
  }
}
```

### Grid System

**CSS Grid Layout:**
```css
.grid {
  display: grid;
  gap: var(--spacing-4);
}

/* Responsive columns */
.grid--1 { grid-template-columns: 1fr; }
.grid--2 { grid-template-columns: repeat(2, 1fr); }
.grid--3 { grid-template-columns: repeat(3, 1fr); }
.grid--4 { grid-template-columns: repeat(4, 1fr); }

/* Auto-fit responsive grid */
.grid--auto {
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
}

/* Responsive behavior */
@media (max-width: 768px) {
  .grid--2,
  .grid--3,
  .grid--4 {
    grid-template-columns: 1fr;
  }
}

@media (min-width: 768px) and (max-width: 1024px) {
  .grid--3,
  .grid--4 {
    grid-template-columns: repeat(2, 1fr);
  }
}
```

### Image Optimization Data Model

**Image Asset Structure:**
```
main/static/Images/
├── optimized/
│   ├── dishes/
│   │   ├── dish-1.webp          (WebP format)
│   │   ├── dish-1.jpg           (JPEG fallback)
│   │   ├── dish-1-thumb.webp    (Thumbnail)
│   │   └── dish-1-thumb.jpg     (Thumbnail fallback)
│   ├── ui/
│   │   ├── hero-bg.webp
│   │   └── hero-bg.jpg
│   └── sprites/
│       └── icons.svg            (SVG sprite)
└── original/                    (Keep originals for reference)
```

**HTML Picture Element Pattern:**
```html
<picture>
  <source 
    srcset="{% static 'Images/optimized/dishes/dish-1.webp' %}" 
    type="image/webp"
  >
  <source 
    srcset="{% static 'Images/optimized/dishes/dish-1.jpg' %}" 
    type="image/jpeg"
  >
  <img 
    src="{% static 'Images/optimized/dishes/dish-1.jpg' %}" 
    alt="Dish name"
    loading="lazy"
    width="400"
    height="300"
  >
</picture>
```

### Animation State Model

**Animation States:**
```javascript
// Animation state machine
const AnimationStates = {
  IDLE: 'idle',
  LOADING: 'loading',
  SUCCESS: 'success',
  ERROR: 'error',
  DISABLED: 'disabled'
};

// State transitions
const stateTransitions = {
  [AnimationStates.IDLE]: [AnimationStates.LOADING, AnimationStates.DISABLED],
  [AnimationStates.LOADING]: [AnimationStates.SUCCESS, AnimationStates.ERROR],
  [AnimationStates.SUCCESS]: [AnimationStates.IDLE],
  [AnimationStates.ERROR]: [AnimationStates.IDLE],
  [AnimationStates.DISABLED]: [AnimationStates.IDLE]
};
```

**CSS State Classes:**
```css
.btn {
  /* Base state */
}

.btn.is-loading {
  pointer-events: none;
  opacity: 0.7;
}

.btn.is-loading::after {
  content: '';
  display: inline-block;
  width: 16px;
  height: 16px;
  margin-left: var(--spacing-2);
  border: 2px solid currentColor;
  border-top-color: transparent;
  border-radius: var(--radius-full);
  animation: spin 0.6s linear infinite;
}

.btn.is-success {
  background-color: var(--color-success);
}

.btn.is-error {
  background-color: var(--color-error);
}
```

### Form Validation Rules Model

**Validation Rule Structure:**
```javascript
const validationRules = {
  email: {
    required: true,
    pattern: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
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
  dishQuantity: {
    required: true,
    min: 1,
    max: 99,
    message: 'Quantity must be between 1 and 99'
  }
};
```

### Page-Specific Data Models

#### Index Page (Home)

**Data Structure:**
```javascript
{
  user: {
    id: number,
    name: string,
    healthScore: number
  },
  recommendations: [
    {
      dishId: number,
      dishName: string,
      imageUrl: string,
      category: string,
      calories: number,
      price: number,
      matchScore: number
    }
  ],
  recentOrders: [
    {
      orderId: number,
      date: string,
      totalAmount: number,
      status: string
    }
  ]
}
```

#### Orders Page

**Data Structure:**
```javascript
{
  categories: ['meat', 'vegetables', 'staples'],
  dishes: [
    {
      id: number,
      name: string,
      category: string,
      imageUrl: string,
      price: number,
      calories: number,
      protein: number,
      carbs: number,
      fat: number,
      description: string,
      available: boolean
    }
  ],
  cart: [
    {
      dishId: number,
      quantity: number,
      price: number
    }
  ],
  cartTotal: number
}
```

#### Profile Page

**Data Structure:**
```javascript
{
  user: {
    id: number,
    username: string,
    email: string,
    phone: string,
    avatar: string,
    healthProfile: {
      age: number,
      gender: string,
      height: number,
      weight: number,
      activityLevel: string,
      dietaryRestrictions: string[]
    }
  }
}
```

#### Nutrition Reports Page

**Data Structure:**
```javascript
{
  period: 'daily' | 'weekly' | 'monthly',
  nutritionData: {
    calories: {
      consumed: number,
      target: number,
      percentage: number
    },
    protein: {
      consumed: number,
      target: number,
      unit: 'g'
    },
    carbs: {
      consumed: number,
      target: number,
      unit: 'g'
    },
    fat: {
      consumed: number,
      target: number,
      unit: 'g'
    }
  },
  healthScore: number,
  chartData: [
    {
      date: string,
      calories: number,
      protein: number,
      carbs: number,
      fat: number
    }
  ]
}
```

### Django Template Context Model

**Base Template Context:**
```python
# Context passed to all templates via base.html
{
    'user': {
        'is_authenticated': bool,
        'username': str,
        'user_id': int
    },
    'current_page': str,  # For navigation highlighting
    'site_name': 'DashBoard',
    'static_version': str  # For cache busting
}
```

**Template Inheritance Structure:**
```
base.html (Base template with design system)
├── index.html (Home page)
├── orders.html (Orders page)
├── profile.html (Profile page)
├── repo.html (Reports page)
├── order_history.html (History page)
├── ai_health_advisor.html (AI Advisor page)
└── login.html (Login page - minimal layout)
```

## Error Handling

### CSS Fallback Strategies

**Browser Compatibility Fallbacks:**
```css
/* Flexbox with float fallback */
.container {
  float: left; /* Fallback for old browsers */
  display: flex; /* Modern browsers */
}

/* Grid with flexbox fallback */
.grid {
  display: flex; /* Fallback */
  flex-wrap: wrap;
  display: grid; /* Modern browsers override */
}

/* CSS custom properties with fallbacks */
.button {
  background-color: #10b981; /* Fallback */
  background-color: var(--color-primary); /* Modern browsers */
}

/* WebP with JPEG fallback (handled in HTML) */
```

**Graceful Degradation for Animations:**
```css
/* Respect user preferences for reduced motion */
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

### JavaScript Error Handling

**Lazy Loading Fallback:**
```javascript
// Fallback for browsers without IntersectionObserver
if (!('IntersectionObserver' in window)) {
  // Load all images immediately
  document.querySelectorAll('img[loading="lazy"]').forEach(img => {
    img.src = img.dataset.src || img.src;
  });
}
```

**Form Validation Fallback:**
```javascript
// Ensure HTML5 validation works even if JS fails
// Forms have native HTML5 validation attributes
<input type="email" required pattern="[^@]+@[^@]+\.[^@]+">
```

**Toast Notification Fallback:**
```javascript
// If toast system fails, use native alert
try {
  window.toast.show('Success message', 'success');
} catch (error) {
  alert('Success message');
}
```

### Network Error Handling

**API Request Error Handling:**
```javascript
async function submitOrder(orderData) {
  const button = document.querySelector('#submit-order');
  button.classList.add('is-loading');
  button.disabled = true;
  
  try {
    const response = await fetch('/api/submit_order/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken')
      },
      body: JSON.stringify(orderData)
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    
    if (data.success) {
      window.toast.show('Order submitted successfully', 'success');
      // Redirect or update UI
    } else {
      throw new Error(data.message || 'Order submission failed');
    }
    
  } catch (error) {
    console.error('Order submission error:', error);
    window.toast.show(
      error.message || 'Failed to submit order. Please try again.',
      'error'
    );
  } finally {
    button.classList.remove('is-loading');
    button.disabled = false;
  }
}
```

**Image Loading Error Handling:**
```javascript
// Handle image load failures
document.querySelectorAll('img').forEach(img => {
  img.addEventListener('error', function() {
    // Replace with placeholder image
    this.src = '/static/Images/placeholder.jpg';
    this.alt = 'Image not available';
  });
});
```

### Accessibility Error Prevention

**Keyboard Navigation:**
```javascript
// Ensure all interactive elements are keyboard accessible
document.querySelectorAll('.card').forEach(card => {
  card.setAttribute('tabindex', '0');
  card.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      card.click();
    }
  });
});
```

**Screen Reader Announcements:**
```javascript
// Announce dynamic content changes to screen readers
function announceToScreenReader(message) {
  const announcement = document.createElement('div');
  announcement.setAttribute('role', 'status');
  announcement.setAttribute('aria-live', 'polite');
  announcement.className = 'sr-only';
  announcement.textContent = message;
  document.body.appendChild(announcement);
  
  setTimeout(() => {
    announcement.remove();
  }, 1000);
}
```

## Testing Strategy

### Dual Testing Approach

The frontend UI optimization will use a combination of manual testing, automated testing, and property-based testing to ensure comprehensive coverage:

**Manual Testing:**
- Visual regression testing across different browsers and devices
- User experience testing with real users
- Accessibility testing with screen readers and keyboard navigation

**Automated Testing:**
- Unit tests for JavaScript modules (form validation, lazy loading, toast notifications)
- Integration tests for component interactions
- End-to-end tests for critical user flows

**Property-Based Testing:**
- Universal properties that should hold across all inputs and states
- Randomized testing to catch edge cases

### Testing Tools and Frameworks

**Browser Testing:**
- Chrome DevTools for debugging and performance profiling
- Firefox Developer Tools for CSS Grid/Flexbox inspection
- Safari Web Inspector for iOS compatibility
- Edge DevTools for Windows compatibility

**Automated Testing:**
- Jest or Mocha for JavaScript unit tests
- Playwright or Cypress for end-to-end tests
- Lighthouse CI for performance regression testing

**Accessibility Testing:**
- axe DevTools for automated accessibility scanning
- NVDA or JAWS screen readers for manual testing
- Keyboard-only navigation testing

**Performance Testing:**
- Google Lighthouse for performance, accessibility, SEO scores
- WebPageTest for detailed performance metrics
- Chrome DevTools Performance panel for runtime analysis

### Unit Testing Strategy

**JavaScript Module Tests:**

Each JavaScript module should have corresponding unit tests:

```javascript
// form-validation.test.js
describe('FormValidator', () => {
  test('validates required fields', () => {
    const validator = new FormValidator(form, {
      email: { required: true }
    });
    expect(validator.validateField('email', '')).toEqual({
      valid: false,
      message: 'email is required'
    });
  });
  
  test('validates email pattern', () => {
    const validator = new FormValidator(form, {
      email: {
        pattern: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
        message: 'Invalid email'
      }
    });
    expect(validator.validateField('email', 'invalid')).toEqual({
      valid: false,
      message: 'Invalid email'
    });
    expect(validator.validateField('email', 'test@example.com')).toEqual({
      valid: true
    });
  });
});
```

**CSS Component Tests:**

Visual regression tests to ensure components render correctly:

```javascript
// Using Playwright for visual regression
test('button component renders correctly', async ({ page }) => {
  await page.goto('/test/components/button');
  await expect(page.locator('.btn--primary')).toHaveScreenshot('button-primary.png');
  await expect(page.locator('.btn--secondary')).toHaveScreenshot('button-secondary.png');
});
```

### Integration Testing Strategy

**Component Interaction Tests:**

Test how components work together:

```javascript
test('form submission with validation', async ({ page }) => {
  await page.goto('/orders');
  
  // Try to submit empty form
  await page.click('#submit-order');
  await expect(page.locator('.form-field__error')).toBeVisible();
  
  // Fill form correctly
  await page.fill('#dish-quantity', '2');
  await page.click('#submit-order');
  
  // Check success toast appears
  await expect(page.locator('.toast--success')).toBeVisible();
});
```

**Navigation Flow Tests:**

```javascript
test('navigation between pages', async ({ page }) => {
  await page.goto('/');
  
  // Navigate to orders page
  await page.click('a[href="/orders"]');
  await expect(page).toHaveURL('/orders');
  await expect(page.locator('.navbar__link--active')).toHaveText('Orders');
  
  // Navigate to profile
  await page.click('a[href="/profile"]');
  await expect(page).toHaveURL('/profile');
  await expect(page.locator('.navbar__link--active')).toHaveText('Profile');
});
```

### Property-Based Testing Configuration

**Test Configuration:**
- Minimum 100 iterations per property test
- Each property test references its design document property
- Tag format: `Feature: frontend-ui-optimization, Property {number}: {property_text}`

**Property Test Example:**

```javascript
// Using fast-check for property-based testing
const fc = require('fast-check');

// Feature: frontend-ui-optimization, Property 1: Color contrast ratios
test('all text colors meet WCAG contrast requirements', () => {
  fc.assert(
    fc.property(
      fc.hexaColor(), // Generate random background color
      fc.hexaColor(), // Generate random text color
      (bgColor, textColor) => {
        const contrast = calculateContrastRatio(bgColor, textColor);
        // For normal text, contrast must be at least 4.5:1
        return contrast >= 4.5;
      }
    ),
    { numRuns: 100 }
  );
});
```

### Performance Testing Strategy

**Lighthouse Metrics:**

Target scores for each page:
- Performance: ≥ 85
- Accessibility: ≥ 95
- Best Practices: ≥ 90
- SEO: ≥ 90

**Core Web Vitals:**
- Largest Contentful Paint (LCP): < 2.5s
- First Input Delay (FID): < 100ms
- Cumulative Layout Shift (CLS): < 0.1

**Performance Budget:**
- Total page weight: < 2MB
- JavaScript bundle: < 200KB
- CSS bundle: < 100KB
- Images: < 1.5MB (with lazy loading)

### Cross-Browser Testing Matrix

**Desktop Browsers:**
- Chrome (latest 2 versions)
- Firefox (latest 2 versions)
- Safari (latest 2 versions)
- Edge (latest 2 versions)

**Mobile Browsers:**
- Chrome Mobile (Android)
- Safari Mobile (iOS)
- Samsung Internet

**Screen Sizes:**
- Mobile: 375px, 414px
- Tablet: 768px, 1024px
- Desktop: 1280px, 1920px

### Accessibility Testing Checklist

**Automated Tests:**
- Run axe DevTools on all pages
- Check color contrast ratios
- Verify ARIA labels and roles
- Check heading hierarchy

**Manual Tests:**
- Keyboard-only navigation through all pages
- Screen reader testing (NVDA/JAWS)
- Test with 200% text zoom
- Test with high contrast mode
- Test with reduced motion preferences

### Test Execution Plan

**Phase 1: Component Testing (Week 1)**
- Unit test all JavaScript modules
- Visual regression test all components
- Accessibility test all components

**Phase 2: Integration Testing (Week 2)**
- Test component interactions
- Test navigation flows
- Test form submissions

**Phase 3: Cross-Browser Testing (Week 3)**
- Test on all target browsers
- Test on all target screen sizes
- Fix browser-specific issues

**Phase 4: Performance Testing (Week 4)**
- Run Lighthouse on all pages
- Optimize based on results
- Verify Core Web Vitals

**Phase 5: User Acceptance Testing (Week 5)**
- Conduct user testing sessions
- Gather feedback
- Make final adjustments

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Acceptance Criteria Testing Prework

Before defining correctness properties, I analyzed each acceptance criterion for testability:

**Requirement 1 (Design System):**
- 1.1-1.7: Design system definitions - These are structural requirements, not runtime behaviors. Testable through code review and CSS validation, not property tests.

**Requirement 2 (Responsive Layout):**
- 2.1-2.7: Responsive breakpoints and layouts - Testable through visual regression tests and viewport testing, but not ideal for property-based testing (specific breakpoint values).

**Requirement 3 (Navigation):**
- 3.1-3.6: Navigation behavior - Some testable as properties (consistency, highlighting), others are performance requirements.

**Requirement 4 (Card Layout):**
- 4.1-4.6: Card component behavior - Testable through visual regression, not property-based.

**Requirement 5 (Animations):**
- 5.1-5.7: Animation behavior - Timing and performance requirements, testable but not as properties.

**Requirement 6 (Form Validation):**
- 6.1-6.7: Form validation behavior - **HIGHLY TESTABLE** as properties! Validation rules should hold for all inputs.

**Requirement 7 (Visual Hierarchy):**
- 7.1-7.7: Visual design requirements - Contrast ratios are testable as properties!

**Requirement 8 (UI Libraries):**
- 8.1-8.6: Library integration - Structural requirements, not runtime properties.

**Requirement 9 (Image Optimization):**
- 9.1-9.7: Image handling - File format and optimization, testable but not as properties.

**Requirement 10 (Performance):**
- 10.1-10.7: Performance metrics - Measurable but specific thresholds, not universal properties.

**Requirement 11 (SEO):**
- 11.1-11.7: SEO metadata - Testable through HTML validation, not properties.

**Requirement 12 (Accessibility):**
- 12.1-12.7: Accessibility compliance - **TESTABLE** as properties! ARIA labels, keyboard navigation should work for all elements.

**Requirement 13 (Cross-Browser):**
- 13.1-13.6: Browser compatibility - Testable through cross-browser testing, not properties.

**Requirement 14 (Theme Consistency):**
- 14.1-14.7: Consistency across pages - Testable through visual regression, not properties.

**Requirement 15 (User Feedback):**
- 15.1-15.7: Interaction feedback - Testable through integration tests, not properties.

**Requirement 16 (Testing):**
- 16.1-16.7: Testing process - Meta-requirements about testing itself.

**Requirement 17 (Documentation):**
- 17.1-17.7: Documentation requirements - Not runtime behavior.

### Property Reflection

After analyzing all acceptance criteria, the following are suitable for property-based testing:

1. **Form validation rules** (Req 6) - Universal validation logic
2. **Color contrast ratios** (Req 7.3) - Must hold for all color combinations
3. **Keyboard accessibility** (Req 12.2) - All interactive elements must be keyboard navigable
4. **ARIA label presence** (Req 12.3) - All interactive elements must have proper labels

Many other requirements are better tested through:
- Visual regression testing (layout, design, consistency)
- Integration testing (navigation, interactions)
- Performance testing (load times, metrics)
- Manual testing (user experience, cross-browser)

### Correctness Properties

#### Property 1: Form Validation Consistency

*For any* form field with validation rules, when invalid data is entered and the field loses focus, the form SHALL display an error message and prevent submission.

**Validates: Requirements 6.2, 6.3, 6.4**

**Test Implementation:**
```javascript
// Feature: frontend-ui-optimization, Property 1: Form validation consistency
fc.assert(
  fc.property(
    fc.record({
      fieldType: fc.constantFrom('email', 'password', 'phone', 'number'),
      invalidValue: fc.string()
    }),
    ({ fieldType, invalidValue }) => {
      const validator = new FormValidator(form, validationRules);
      const result = validator.validateField(fieldType, invalidValue);
      
      // If value doesn't match the pattern, validation should fail
      if (!validationRules[fieldType].pattern.test(invalidValue)) {
        return result.valid === false && result.message.length > 0;
      }
      return true;
    }
  ),
  { numRuns: 100 }
);
```

#### Property 2: Color Contrast Compliance

*For any* text element and its background, the color contrast ratio SHALL be at least 4.5:1 for normal text and 3:1 for large text to meet WCAG AA standards.

**Validates: Requirements 7.3**

**Test Implementation:**
```javascript
// Feature: frontend-ui-optimization, Property 2: Color contrast compliance
test('all design system colors meet contrast requirements', () => {
  const colorPairs = [
    { text: '--color-text-primary', bg: '--color-background' },
    { text: '--color-text-secondary', bg: '--color-background' },
    { text: 'white', bg: '--color-primary' },
    { text: '--color-text-primary', bg: '--color-surface' }
  ];
  
  colorPairs.forEach(pair => {
    const textColor = getComputedColor(pair.text);
    const bgColor = getComputedColor(pair.bg);
    const contrast = calculateContrastRatio(textColor, bgColor);
    
    expect(contrast).toBeGreaterThanOrEqual(4.5);
  });
});
```

#### Property 3: Keyboard Navigation Completeness

*For any* interactive element (buttons, links, form fields, cards), the element SHALL be reachable and operable using only keyboard navigation (Tab, Enter, Space keys).

**Validates: Requirements 12.2**

**Test Implementation:**
```javascript
// Feature: frontend-ui-optimization, Property 3: Keyboard navigation completeness
test('all interactive elements are keyboard accessible', async ({ page }) => {
  await page.goto('/orders');
  
  const interactiveElements = await page.locator(
    'button, a, input, select, textarea, [role="button"], .card'
  ).all();
  
  for (const element of interactiveElements) {
    // Element should have tabindex (0 or positive)
    const tabindex = await element.getAttribute('tabindex');
    const isNaturallyFocusable = await element.evaluate(el => 
      ['BUTTON', 'A', 'INPUT', 'SELECT', 'TEXTAREA'].includes(el.tagName)
    );
    
    expect(isNaturallyFocusable || tabindex !== null).toBe(true);
    
    // Element should be focusable
    await element.focus();
    const isFocused = await element.evaluate(el => el === document.activeElement);
    expect(isFocused).toBe(true);
  }
});
```

#### Property 4: ARIA Label Presence

*For any* interactive element without visible text content, the element SHALL have an appropriate ARIA label or aria-labelledby attribute for screen reader accessibility.

**Validates: Requirements 12.3**

**Test Implementation:**
```javascript
// Feature: frontend-ui-optimization, Property 4: ARIA label presence
test('all interactive elements have accessible names', async ({ page }) => {
  await page.goto('/');
  
  const pages = ['/', '/orders', '/profile', '/repo', '/order_history', '/ai_health_advisor'];
  
  for (const pagePath of pages) {
    await page.goto(pagePath);
    
    const interactiveElements = await page.locator(
      'button, a[href], input, select, textarea, [role="button"]'
    ).all();
    
    for (const element of interactiveElements) {
      const accessibleName = await element.evaluate(el => {
        // Check for visible text
        const text = el.textContent?.trim();
        if (text) return text;
        
        // Check for aria-label
        const ariaLabel = el.getAttribute('aria-label');
        if (ariaLabel) return ariaLabel;
        
        // Check for aria-labelledby
        const labelledBy = el.getAttribute('aria-labelledby');
        if (labelledBy) {
          const labelElement = document.getElementById(labelledBy);
          return labelElement?.textContent?.trim();
        }
        
        // Check for associated label (for inputs)
        if (el.tagName === 'INPUT') {
          const id = el.getAttribute('id');
          if (id) {
            const label = document.querySelector(`label[for="${id}"]`);
            return label?.textContent?.trim();
          }
        }
        
        // Check for alt text (for image buttons)
        const alt = el.getAttribute('alt');
        if (alt) return alt;
        
        return null;
      });
      
      expect(accessibleName).toBeTruthy();
    }
  }
});
```

#### Property 5: Form Validation Round Trip

*For any* valid form data, when the data is entered, validated, and submitted, the validation SHALL pass and the form SHALL be submittable without errors.

**Validates: Requirements 6.1, 6.3, 6.7**

**Test Implementation:**
```javascript
// Feature: frontend-ui-optimization, Property 5: Form validation round trip
fc.assert(
  fc.property(
    fc.record({
      email: fc.emailAddress(),
      password: fc.string({ minLength: 8 }).filter(s => 
        /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/.test(s)
      ),
      quantity: fc.integer({ min: 1, max: 99 })
    }),
    (validData) => {
      const validator = new FormValidator(form, validationRules);
      
      // Validate each field
      const emailResult = validator.validateField('email', validData.email);
      const passwordResult = validator.validateField('password', validData.password);
      const quantityResult = validator.validateField('quantity', validData.quantity.toString());
      
      // All validations should pass for valid data
      return emailResult.valid && passwordResult.valid && quantityResult.valid;
    }
  ),
  { numRuns: 100 }
);
```

#### Property 6: Responsive Breakpoint Consistency

*For any* viewport width, the page SHALL apply exactly one breakpoint's styles (mobile, tablet, or desktop) without overlapping or conflicting styles.

**Validates: Requirements 2.2, 2.3, 2.4**

**Test Implementation:**
```javascript
// Feature: frontend-ui-optimization, Property 6: Responsive breakpoint consistency
test('responsive breakpoints apply correct styles', async ({ page }) => {
  const breakpoints = [
    { width: 375, name: 'mobile' },
    { width: 768, name: 'tablet' },
    { width: 1024, name: 'desktop' },
    { width: 1920, name: 'desktop-large' }
  ];
  
  for (const breakpoint of breakpoints) {
    await page.setViewportSize({ width: breakpoint.width, height: 800 });
    await page.goto('/orders');
    
    const container = page.locator('.container');
    const padding = await container.evaluate(el => 
      window.getComputedStyle(el).padding
    );
    
    // Verify padding matches expected breakpoint
    if (breakpoint.width < 768) {
      expect(padding).toContain('16px'); // Mobile padding
    } else if (breakpoint.width < 1024) {
      expect(padding).toContain('24px'); // Tablet padding
    } else {
      expect(padding).toContain('32px'); // Desktop padding
    }
  }
});
```

#### Property 7: Image Lazy Loading Behavior

*For any* image with `loading="lazy"` attribute that is below the viewport, the image SHALL not load until it enters the viewport (within the root margin threshold).

**Validates: Requirements 9.3**

**Test Implementation:**
```javascript
// Feature: frontend-ui-optimization, Property 7: Image lazy loading behavior
test('images lazy load when entering viewport', async ({ page }) => {
  await page.goto('/orders');
  
  // Get all lazy-loaded images
  const lazyImages = await page.locator('img[loading="lazy"]').all();
  
  for (const img of lazyImages) {
    const isInViewport = await img.evaluate(el => {
      const rect = el.getBoundingClientRect();
      return rect.top < window.innerHeight && rect.bottom > 0;
    });
    
    const isLoaded = await img.evaluate(el => el.complete && el.naturalHeight > 0);
    
    // Images outside viewport should not be loaded yet
    if (!isInViewport) {
      expect(isLoaded).toBe(false);
    }
    
    // Scroll image into view
    await img.scrollIntoViewIfNeeded();
    await page.waitForTimeout(500); // Wait for lazy load
    
    // Image should now be loaded
    const isLoadedAfterScroll = await img.evaluate(el => 
      el.complete && el.naturalHeight > 0
    );
    expect(isLoadedAfterScroll).toBe(true);
  }
});
```

### Testing Notes

**Property-Based Testing Limitations:**

Many of the UI optimization requirements are better suited for other testing approaches:

1. **Visual Regression Testing**: Layout consistency, component styling, theme uniformity
2. **Integration Testing**: Navigation flows, form submissions, user interactions
3. **Performance Testing**: Load times, Core Web Vitals, Lighthouse scores
4. **Manual Testing**: User experience, visual design quality, cross-browser compatibility

**Recommended Testing Distribution:**
- Property-Based Tests: 10% (validation logic, accessibility rules, contrast ratios)
- Unit Tests: 20% (JavaScript modules, utility functions)
- Integration Tests: 30% (component interactions, user flows)
- Visual Regression Tests: 25% (layout, styling, consistency)
- Manual Testing: 15% (UX, design quality, edge cases)

This distribution ensures comprehensive coverage while using the most appropriate testing method for each requirement type.

