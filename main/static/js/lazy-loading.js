/**
 * Lazy Loading Module
 * 
 * Implements efficient image lazy loading using IntersectionObserver API
 * with fallback for browsers that don't support it.
 * 
 * Usage:
 *   const lazyLoader = new LazyLoader({
 *     rootMargin: '50px',
 *     threshold: 0.01
 *   });
 *   lazyLoader.init();
 * 
 * HTML:
 *   <img src="placeholder.jpg" data-src="actual-image.jpg" loading="lazy" alt="Description">
 */

class LazyLoader {
  /**
   * Initialize the LazyLoader with custom options
   * @param {Object} options - Configuration options
   * @param {string} options.rootMargin - Margin around the viewport for early loading (default: '50px')
   * @param {number} options.threshold - Percentage of visibility required to trigger load (default: 0.01)
   * @param {string} options.loadingClass - CSS class applied while image is loading (default: 'is-loading')
   * @param {string} options.loadedClass - CSS class applied after image loads (default: 'is-loaded')
   */
  constructor(options = {}) {
    this.options = {
      rootMargin: options.rootMargin || '50px',
      threshold: options.threshold || 0.01,
      loadingClass: options.loadingClass || 'is-loading',
      loadedClass: options.loadedClass || 'is-loaded'
    };
    
    this.observer = null;
  }
  
  /**
   * Initialize the lazy loader
   * Sets up IntersectionObserver if supported, otherwise falls back to loading all images
   */
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
      // Fallback: load all images immediately for browsers without IntersectionObserver
      console.warn('IntersectionObserver not supported, loading all images immediately');
      this.loadAllImages();
    }
  }
  
  /**
   * Find and observe all lazy-loadable images
   * Images should have loading="lazy" attribute
   */
  observeImages() {
    const images = document.querySelectorAll('img[loading="lazy"]');
    
    images.forEach(img => {
      // Add loading class to indicate image is pending
      img.classList.add(this.options.loadingClass);
      
      // Start observing the image
      this.observer.observe(img);
    });
    
    console.log(`LazyLoader: Observing ${images.length} images`);
  }
  
  /**
   * Handle intersection events from the IntersectionObserver
   * @param {IntersectionObserverEntry[]} entries - Array of intersection entries
   */
  handleIntersection(entries) {
    entries.forEach(entry => {
      // Check if the image has entered the viewport
      if (entry.isIntersecting) {
        const img = entry.target;
        
        // Load the image
        this.loadImage(img);
        
        // Stop observing this image
        this.observer.unobserve(img);
      }
    });
  }
  
  /**
   * Load a single image
   * @param {HTMLImageElement} img - The image element to load
   */
  loadImage(img) {
    // Get the actual source from data-src attribute, or use existing src
    const src = img.dataset.src || img.src;
    const srcset = img.dataset.srcset;
    
    // Set up load event handler
    img.addEventListener('load', () => {
      // Remove loading class and add loaded class
      img.classList.remove(this.options.loadingClass);
      img.classList.add(this.options.loadedClass);
    });
    
    // Set up error event handler
    img.addEventListener('error', () => {
      // Remove loading class
      img.classList.remove(this.options.loadingClass);
      
      // Set placeholder image on error
      img.src = '/static/Images/placeholder.jpg';
      img.alt = 'Image not available';
      
      console.error(`LazyLoader: Failed to load image: ${src}`);
    });
    
    // Update the src to trigger loading
    if (src && src !== img.src) {
      img.src = src;
    }
    
    // Update srcset if provided
    if (srcset) {
      img.srcset = srcset;
    }
  }
  
  /**
   * Fallback method: Load all images immediately
   * Used when IntersectionObserver is not supported
   */
  loadAllImages() {
    const images = document.querySelectorAll('img[loading="lazy"]');
    
    images.forEach(img => {
      this.loadImage(img);
    });
    
    console.log(`LazyLoader: Loaded ${images.length} images (fallback mode)`);
  }
  
  /**
   * Manually trigger loading of a specific image
   * Useful for dynamically added images
   * @param {HTMLImageElement} img - The image element to load
   */
  loadImageManually(img) {
    if (this.observer) {
      this.observer.unobserve(img);
    }
    this.loadImage(img);
  }
  
  /**
   * Add new images to the observer
   * Useful for dynamically added content
   */
  refresh() {
    if (this.observer) {
      // Find images that aren't already being observed
      const images = document.querySelectorAll('img[loading="lazy"]:not(.is-loading):not(.is-loaded)');
      
      images.forEach(img => {
        img.classList.add(this.options.loadingClass);
        this.observer.observe(img);
      });
      
      if (images.length > 0) {
        console.log(`LazyLoader: Added ${images.length} new images to observer`);
      }
    }
  }
  
  /**
   * Disconnect the observer and clean up
   */
  destroy() {
    if (this.observer) {
      this.observer.disconnect();
      this.observer = null;
      console.log('LazyLoader: Observer disconnected');
    }
  }
}

// Export for use in other modules (if using module system)
if (typeof module !== 'undefined' && module.exports) {
  module.exports = LazyLoader;
}

// Make available globally
if (typeof window !== 'undefined') {
  window.LazyLoader = LazyLoader;
}
