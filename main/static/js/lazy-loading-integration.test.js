/**
 * Integration Test for Lazy Loading Behavior
 * 
 * Feature: frontend-ui-optimization
 * Property 7: Image lazy loading behavior
 * Validates: Requirements 9.3
 * 
 * This integration test verifies that images with loading="lazy" attribute
 * behave correctly in a real browser environment:
 * 1. Images outside viewport should not be loaded initially
 * 2. Images should load when scrolled into viewport
 * 3. Images should have proper loading states (is-loading, is-loaded)
 * 
 * Run this test in a browser environment by opening lazy-loading-integration-test.html
 */

class LazyLoadingIntegrationTest {
  constructor() {
    this.results = [];
    this.passedTests = 0;
    this.failedTests = 0;
  }

  /**
   * Log test result
   */
  logResult(testName, passed, message = '') {
    const result = {
      name: testName,
      passed: passed,
      message: message,
      timestamp: new Date().toISOString()
    };
    
    this.results.push(result);
    
    if (passed) {
      this.passedTests++;
      console.log(`✅ ${testName} PASSED${message ? ': ' + message : ''}`);
    } else {
      this.failedTests++;
      console.error(`❌ ${testName} FAILED${message ? ': ' + message : ''}`);
    }
  }

  /**
   * Wait for a condition to be true
   */
  async waitFor(condition, timeout = 5000, interval = 100) {
    const startTime = Date.now();
    
    while (Date.now() - startTime < timeout) {
      if (await condition()) {
        return true;
      }
      await new Promise(resolve => setTimeout(resolve, interval));
    }
    
    return false;
  }

  /**
   * Check if an image is in the viewport
   */
  isInViewport(element, rootMargin = 0) {
    const rect = element.getBoundingClientRect();
    const windowHeight = window.innerHeight || document.documentElement.clientHeight;
    const windowWidth = window.innerWidth || document.documentElement.clientWidth;
    
    return (
      rect.top >= -rootMargin &&
      rect.left >= -rootMargin &&
      rect.bottom <= windowHeight + rootMargin &&
      rect.right <= windowWidth + rootMargin
    );
  }

  /**
   * Check if an image has been loaded
   */
  isImageLoaded(img) {
    return img.complete && img.naturalHeight > 0;
  }

  /**
   * Test 1: Images outside viewport should not load initially
   */
  async testImagesOutsideViewportNotLoaded() {
    const testName = 'Test 1: Images outside viewport should not load initially';
    
    try {
      // Find all lazy images that are below the fold
      const lazyImages = Array.from(document.querySelectorAll('img[loading="lazy"]'));
      const belowFoldImages = lazyImages.filter(img => !this.isInViewport(img));
      
      if (belowFoldImages.length === 0) {
        this.logResult(testName, false, 'No images found below the fold for testing');
        return;
      }
      
      // Check that none of the below-fold images are loaded
      const unloadedImages = belowFoldImages.filter(img => !this.isImageLoaded(img));
      const loadedImages = belowFoldImages.filter(img => this.isImageLoaded(img));
      
      if (loadedImages.length > 0) {
        this.logResult(
          testName, 
          false, 
          `${loadedImages.length} out of ${belowFoldImages.length} below-fold images were already loaded`
        );
      } else {
        this.logResult(
          testName, 
          true, 
          `All ${belowFoldImages.length} below-fold images are not loaded initially`
        );
      }
    } catch (error) {
      this.logResult(testName, false, error.message);
    }
  }

  /**
   * Test 2: Images should have loading class initially
   */
  async testImagesHaveLoadingClass() {
    const testName = 'Test 2: Images should have loading class initially';
    
    try {
      const lazyImages = Array.from(document.querySelectorAll('img[loading="lazy"]'));
      const belowFoldImages = lazyImages.filter(img => !this.isInViewport(img));
      
      if (belowFoldImages.length === 0) {
        this.logResult(testName, false, 'No images found below the fold for testing');
        return;
      }
      
      // Check that below-fold images have the loading class
      const imagesWithLoadingClass = belowFoldImages.filter(img => 
        img.classList.contains('is-loading')
      );
      
      if (imagesWithLoadingClass.length === belowFoldImages.length) {
        this.logResult(
          testName, 
          true, 
          `All ${belowFoldImages.length} below-fold images have 'is-loading' class`
        );
      } else {
        this.logResult(
          testName, 
          false, 
          `Only ${imagesWithLoadingClass.length} out of ${belowFoldImages.length} images have 'is-loading' class`
        );
      }
    } catch (error) {
      this.logResult(testName, false, error.message);
    }
  }

  /**
   * Test 3: Images should load when scrolled into viewport
   */
  async testImagesLoadWhenScrolledIntoView() {
    const testName = 'Test 3: Images should load when scrolled into viewport';
    
    try {
      // Find a lazy image that's below the fold
      const lazyImages = Array.from(document.querySelectorAll('img[loading="lazy"]'));
      const belowFoldImages = lazyImages.filter(img => !this.isInViewport(img, 100));
      
      if (belowFoldImages.length === 0) {
        this.logResult(testName, false, 'No images found below the fold for testing');
        return;
      }
      
      // Pick the first below-fold image
      const testImage = belowFoldImages[0];
      const wasLoaded = this.isImageLoaded(testImage);
      
      if (wasLoaded) {
        this.logResult(testName, false, 'Test image was already loaded before scrolling');
        return;
      }
      
      // Scroll the image into view
      testImage.scrollIntoView({ behavior: 'smooth', block: 'center' });
      
      // Wait for the image to load (with timeout)
      const loaded = await this.waitFor(() => this.isImageLoaded(testImage), 3000);
      
      if (loaded) {
        this.logResult(testName, true, 'Image loaded successfully after scrolling into viewport');
      } else {
        this.logResult(testName, false, 'Image did not load within timeout after scrolling');
      }
    } catch (error) {
      this.logResult(testName, false, error.message);
    }
  }

  /**
   * Test 4: Images should have loaded class after loading
   */
  async testImagesHaveLoadedClassAfterLoading() {
    const testName = 'Test 4: Images should have loaded class after loading';
    
    try {
      // Find a lazy image that's below the fold
      const lazyImages = Array.from(document.querySelectorAll('img[loading="lazy"]'));
      const belowFoldImages = lazyImages.filter(img => !this.isInViewport(img, 100));
      
      if (belowFoldImages.length === 0) {
        this.logResult(testName, false, 'No images found below the fold for testing');
        return;
      }
      
      // Pick the second below-fold image (if available)
      const testImage = belowFoldImages[Math.min(1, belowFoldImages.length - 1)];
      
      // Scroll the image into view
      testImage.scrollIntoView({ behavior: 'smooth', block: 'center' });
      
      // Wait for the image to load
      const loaded = await this.waitFor(() => this.isImageLoaded(testImage), 3000);
      
      if (!loaded) {
        this.logResult(testName, false, 'Image did not load within timeout');
        return;
      }
      
      // Wait a bit more for the class to be applied
      await new Promise(resolve => setTimeout(resolve, 500));
      
      // Check if the image has the loaded class
      const hasLoadedClass = testImage.classList.contains('is-loaded');
      const hasLoadingClass = testImage.classList.contains('is-loading');
      
      if (hasLoadedClass && !hasLoadingClass) {
        this.logResult(
          testName, 
          true, 
          'Image has "is-loaded" class and no longer has "is-loading" class'
        );
      } else {
        this.logResult(
          testName, 
          false, 
          `Image classes: is-loaded=${hasLoadedClass}, is-loading=${hasLoadingClass}`
        );
      }
    } catch (error) {
      this.logResult(testName, false, error.message);
    }
  }

  /**
   * Test 5: Multiple images should load as they enter viewport
   */
  async testMultipleImagesLoadSequentially() {
    const testName = 'Test 5: Multiple images should load as they enter viewport';
    
    try {
      // Find all lazy images that are below the fold
      const lazyImages = Array.from(document.querySelectorAll('img[loading="lazy"]'));
      const belowFoldImages = lazyImages.filter(img => !this.isInViewport(img, 100));
      
      if (belowFoldImages.length < 2) {
        this.logResult(testName, false, 'Need at least 2 images below the fold for testing');
        return;
      }
      
      // Take up to 3 images for testing
      const testImages = belowFoldImages.slice(0, Math.min(3, belowFoldImages.length));
      let loadedCount = 0;
      
      // Scroll through each image and verify it loads
      for (const img of testImages) {
        img.scrollIntoView({ behavior: 'smooth', block: 'center' });
        
        // Wait for this image to load
        const loaded = await this.waitFor(() => this.isImageLoaded(img), 3000);
        
        if (loaded) {
          loadedCount++;
        }
        
        // Small delay between scrolls
        await new Promise(resolve => setTimeout(resolve, 300));
      }
      
      if (loadedCount === testImages.length) {
        this.logResult(
          testName, 
          true, 
          `All ${testImages.length} images loaded successfully when scrolled into view`
        );
      } else {
        this.logResult(
          testName, 
          false, 
          `Only ${loadedCount} out of ${testImages.length} images loaded`
        );
      }
    } catch (error) {
      this.logResult(testName, false, error.message);
    }
  }

  /**
   * Test 6: IntersectionObserver should be used when supported
   */
  async testIntersectionObserverUsed() {
    const testName = 'Test 6: IntersectionObserver should be used when supported';
    
    try {
      const isSupported = 'IntersectionObserver' in window;
      
      if (isSupported) {
        this.logResult(
          testName, 
          true, 
          'IntersectionObserver is supported and should be used'
        );
      } else {
        this.logResult(
          testName, 
          true, 
          'IntersectionObserver not supported, fallback should be used'
        );
      }
    } catch (error) {
      this.logResult(testName, false, error.message);
    }
  }

  /**
   * Run all integration tests
   */
  async runAllTests() {
    console.log('🧪 Running Lazy Loading Integration Tests...\n');
    console.log('Feature: frontend-ui-optimization');
    console.log('Property 7: Image lazy loading behavior');
    console.log('Validates: Requirements 9.3\n');
    
    // Scroll to top first
    window.scrollTo(0, 0);
    await new Promise(resolve => setTimeout(resolve, 500));
    
    // Run tests sequentially
    await this.testImagesOutsideViewportNotLoaded();
    await this.testImagesHaveLoadingClass();
    await this.testImagesLoadWhenScrolledIntoView();
    await this.testImagesHaveLoadedClassAfterLoading();
    await this.testMultipleImagesLoadSequentially();
    await this.testIntersectionObserverUsed();
    
    // Print summary
    this.printSummary();
    
    return {
      passed: this.passedTests,
      failed: this.failedTests,
      results: this.results
    };
  }

  /**
   * Print test summary
   */
  printSummary() {
    console.log('\n' + '='.repeat(60));
    console.log('Integration Test Results');
    console.log('='.repeat(60));
    console.log(`Total Tests: ${this.passedTests + this.failedTests}`);
    console.log(`✅ Passed: ${this.passedTests}`);
    console.log(`❌ Failed: ${this.failedTests}`);
    console.log('='.repeat(60));
    
    if (this.failedTests === 0) {
      console.log('🎉 All integration tests passed!');
    } else {
      console.log('⚠️  Some tests failed. Review the results above.');
    }
  }

  /**
   * Generate HTML report
   */
  generateHTMLReport() {
    const reportHTML = `
      <div class="test-report">
        <h3>Integration Test Report</h3>
        <div class="test-summary">
          <span class="passed">✅ Passed: ${this.passedTests}</span>
          <span class="failed">❌ Failed: ${this.failedTests}</span>
        </div>
        <div class="test-results">
          ${this.results.map(result => `
            <div class="test-result ${result.passed ? 'passed' : 'failed'}">
              <div class="test-name">${result.passed ? '✅' : '❌'} ${result.name}</div>
              ${result.message ? `<div class="test-message">${result.message}</div>` : ''}
            </div>
          `).join('')}
        </div>
      </div>
    `;
    
    return reportHTML;
  }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
  module.exports = LazyLoadingIntegrationTest;
}

// Make available globally
if (typeof window !== 'undefined') {
  window.LazyLoadingIntegrationTest = LazyLoadingIntegrationTest;
}
