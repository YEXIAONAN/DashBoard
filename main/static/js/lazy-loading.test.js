/**
 * Unit Tests for LazyLoader Module
 * 
 * These tests verify the core functionality of the LazyLoader class
 * Run these tests in a browser environment or with a DOM testing library like jsdom
 */

// Mock IntersectionObserver for testing
class MockIntersectionObserver {
  constructor(callback, options) {
    this.callback = callback;
    this.options = options;
    this.observedElements = [];
  }
  
  observe(element) {
    this.observedElements.push(element);
  }
  
  unobserve(element) {
    const index = this.observedElements.indexOf(element);
    if (index > -1) {
      this.observedElements.splice(index, 1);
    }
  }
  
  disconnect() {
    this.observedElements = [];
  }
  
  // Helper method to simulate intersection
  triggerIntersection(element, isIntersecting) {
    this.callback([{
      target: element,
      isIntersecting: isIntersecting
    }]);
  }
}

// Test Suite
function runTests() {
  console.log('🧪 Running LazyLoader Tests...\n');
  
  let passedTests = 0;
  let failedTests = 0;
  
  // Test 1: Constructor initializes with default options
  try {
    const loader = new LazyLoader();
    
    if (loader.options.rootMargin === '50px' &&
        loader.options.threshold === 0.01 &&
        loader.options.loadingClass === 'is-loading' &&
        loader.options.loadedClass === 'is-loaded') {
      console.log('✅ Test 1 PASSED: Constructor initializes with default options');
      passedTests++;
    } else {
      throw new Error('Default options not set correctly');
    }
  } catch (error) {
    console.error('❌ Test 1 FAILED:', error.message);
    failedTests++;
  }
  
  // Test 2: Constructor accepts custom options
  try {
    const loader = new LazyLoader({
      rootMargin: '100px',
      threshold: 0.5,
      loadingClass: 'custom-loading',
      loadedClass: 'custom-loaded'
    });
    
    if (loader.options.rootMargin === '100px' &&
        loader.options.threshold === 0.5 &&
        loader.options.loadingClass === 'custom-loading' &&
        loader.options.loadedClass === 'custom-loaded') {
      console.log('✅ Test 2 PASSED: Constructor accepts custom options');
      passedTests++;
    } else {
      throw new Error('Custom options not set correctly');
    }
  } catch (error) {
    console.error('❌ Test 2 FAILED:', error.message);
    failedTests++;
  }
  
  // Test 3: init() creates IntersectionObserver when supported
  try {
    // Save original IntersectionObserver
    const originalIO = window.IntersectionObserver;
    window.IntersectionObserver = MockIntersectionObserver;
    
    // Create test DOM
    document.body.innerHTML = `
      <img src="test1.jpg" loading="lazy" alt="Test 1">
      <img src="test2.jpg" loading="lazy" alt="Test 2">
    `;
    
    const loader = new LazyLoader();
    loader.init();
    
    if (loader.observer !== null) {
      console.log('✅ Test 3 PASSED: init() creates IntersectionObserver');
      passedTests++;
    } else {
      throw new Error('Observer not created');
    }
    
    // Restore original IntersectionObserver
    window.IntersectionObserver = originalIO;
  } catch (error) {
    console.error('❌ Test 3 FAILED:', error.message);
    failedTests++;
  }
  
  // Test 4: observeImages() finds and observes lazy images
  try {
    window.IntersectionObserver = MockIntersectionObserver;
    
    document.body.innerHTML = `
      <img src="test1.jpg" loading="lazy" alt="Test 1">
      <img src="test2.jpg" loading="lazy" alt="Test 2">
      <img src="test3.jpg" alt="Test 3">
    `;
    
    const loader = new LazyLoader();
    loader.init();
    
    const lazyImages = document.querySelectorAll('img[loading="lazy"]');
    const observedCount = loader.observer.observedElements.length;
    
    if (observedCount === 2 && lazyImages.length === 2) {
      console.log('✅ Test 4 PASSED: observeImages() finds and observes lazy images');
      passedTests++;
    } else {
      throw new Error(`Expected 2 observed images, got ${observedCount}`);
    }
    
    window.IntersectionObserver = undefined;
  } catch (error) {
    console.error('❌ Test 4 FAILED:', error.message);
    failedTests++;
  }
  
  // Test 5: loadImage() updates src from data-src
  try {
    document.body.innerHTML = `
      <img src="placeholder.jpg" data-src="actual.jpg" loading="lazy" alt="Test">
    `;
    
    const loader = new LazyLoader();
    const img = document.querySelector('img');
    
    loader.loadImage(img);
    
    if (img.src.includes('actual.jpg')) {
      console.log('✅ Test 5 PASSED: loadImage() updates src from data-src');
      passedTests++;
    } else {
      throw new Error('Image src not updated correctly');
    }
  } catch (error) {
    console.error('❌ Test 5 FAILED:', error.message);
    failedTests++;
  }
  
  // Test 6: loadImage() adds loading and loaded classes
  try {
    document.body.innerHTML = `
      <img src="test.jpg" loading="lazy" alt="Test">
    `;
    
    const loader = new LazyLoader();
    const img = document.querySelector('img');
    
    loader.loadImage(img);
    
    // Simulate load event
    img.dispatchEvent(new Event('load'));
    
    if (img.classList.contains('is-loaded') && !img.classList.contains('is-loading')) {
      console.log('✅ Test 6 PASSED: loadImage() adds loaded class after load');
      passedTests++;
    } else {
      throw new Error('Classes not applied correctly');
    }
  } catch (error) {
    console.error('❌ Test 6 FAILED:', error.message);
    failedTests++;
  }
  
  // Test 7: handleIntersection() loads images when intersecting
  try {
    window.IntersectionObserver = MockIntersectionObserver;
    
    document.body.innerHTML = `
      <img src="placeholder.jpg" data-src="actual.jpg" loading="lazy" alt="Test">
    `;
    
    const loader = new LazyLoader();
    loader.init();
    
    const img = document.querySelector('img');
    
    // Simulate intersection
    loader.observer.triggerIntersection(img, true);
    
    if (img.src.includes('actual.jpg')) {
      console.log('✅ Test 7 PASSED: handleIntersection() loads images when intersecting');
      passedTests++;
    } else {
      throw new Error('Image not loaded on intersection');
    }
    
    window.IntersectionObserver = undefined;
  } catch (error) {
    console.error('❌ Test 7 FAILED:', error.message);
    failedTests++;
  }
  
  // Test 8: loadAllImages() fallback works
  try {
    document.body.innerHTML = `
      <img src="placeholder1.jpg" data-src="actual1.jpg" loading="lazy" alt="Test 1">
      <img src="placeholder2.jpg" data-src="actual2.jpg" loading="lazy" alt="Test 2">
    `;
    
    const loader = new LazyLoader();
    loader.loadAllImages();
    
    const images = document.querySelectorAll('img[loading="lazy"]');
    const allLoaded = Array.from(images).every(img => 
      img.src.includes('actual')
    );
    
    if (allLoaded) {
      console.log('✅ Test 8 PASSED: loadAllImages() fallback works');
      passedTests++;
    } else {
      throw new Error('Not all images loaded in fallback mode');
    }
  } catch (error) {
    console.error('❌ Test 8 FAILED:', error.message);
    failedTests++;
  }
  
  // Test 9: refresh() observes new images
  try {
    window.IntersectionObserver = MockIntersectionObserver;
    
    document.body.innerHTML = `
      <img src="test1.jpg" loading="lazy" alt="Test 1">
    `;
    
    const loader = new LazyLoader();
    loader.init();
    
    const initialCount = loader.observer.observedElements.length;
    
    // Add new image
    const newImg = document.createElement('img');
    newImg.src = 'test2.jpg';
    newImg.setAttribute('loading', 'lazy');
    newImg.alt = 'Test 2';
    document.body.appendChild(newImg);
    
    loader.refresh();
    
    const newCount = loader.observer.observedElements.length;
    
    if (newCount > initialCount) {
      console.log('✅ Test 9 PASSED: refresh() observes new images');
      passedTests++;
    } else {
      throw new Error('New images not observed after refresh');
    }
    
    window.IntersectionObserver = undefined;
  } catch (error) {
    console.error('❌ Test 9 FAILED:', error.message);
    failedTests++;
  }
  
  // Test 10: destroy() disconnects observer
  try {
    window.IntersectionObserver = MockIntersectionObserver;
    
    document.body.innerHTML = `
      <img src="test.jpg" loading="lazy" alt="Test">
    `;
    
    const loader = new LazyLoader();
    loader.init();
    
    loader.destroy();
    
    if (loader.observer === null) {
      console.log('✅ Test 10 PASSED: destroy() disconnects observer');
      passedTests++;
    } else {
      throw new Error('Observer not disconnected');
    }
    
    window.IntersectionObserver = undefined;
  } catch (error) {
    console.error('❌ Test 10 FAILED:', error.message);
    failedTests++;
  }
  
  // Print summary
  console.log('\n' + '='.repeat(50));
  console.log(`Test Results: ${passedTests} passed, ${failedTests} failed`);
  console.log('='.repeat(50));
  
  return { passed: passedTests, failed: failedTests };
}

// Run tests if in browser environment
if (typeof window !== 'undefined' && typeof document !== 'undefined') {
  // Wait for DOM to be ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', runTests);
  } else {
    runTests();
  }
}

// Export for Node.js testing
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { runTests };
}
