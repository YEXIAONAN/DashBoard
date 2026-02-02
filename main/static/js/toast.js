/**
 * Toast Notification Module
 * 
 * Provides a ToastManager class for displaying toast notifications
 * with support for different types (success, error, warning, info),
 * auto-dismiss functionality, and screen reader accessibility.
 * 
 * Requirements: 15.3, 15.4, 12.5
 */

class ToastManager {
  constructor(options = {}) {
    this.options = {
      position: options.position || 'top-right',
      defaultDuration: options.defaultDuration || 5000,
      maxToasts: options.maxToasts || 5
    };
    this.container = this.createContainer();
    this.toasts = [];
  }
  
  /**
   * Create toast container element
   * @returns {HTMLElement} The toast container element
   */
  createContainer() {
    let container = document.querySelector('.toast-container');
    if (!container) {
      container = document.createElement('div');
      container.className = `toast-container toast-container--${this.options.position}`;
      container.setAttribute('aria-live', 'polite');
      container.setAttribute('aria-atomic', 'false');
      document.body.appendChild(container);
    }
    return container;
  }
  
  /**
   * Show a toast notification
   * @param {string} message - The message to display
   * @param {string} type - The type of toast (success, error, warning, info)
   * @param {number} duration - Duration in milliseconds (0 for no auto-dismiss)
   * @returns {HTMLElement} The created toast element
   */
  show(message, type = 'success', duration = null) {
    // Use default duration if not specified
    if (duration === null) {
      duration = this.options.defaultDuration;
    }
    
    // Validate type
    const validTypes = ['success', 'error', 'warning', 'info'];
    if (!validTypes.includes(type)) {
      console.warn(`Invalid toast type: ${type}. Using 'info' instead.`);
      type = 'info';
    }
    
    // Remove oldest toast if we've reached the maximum
    if (this.toasts.length >= this.options.maxToasts) {
      this.dismiss(this.toasts[0]);
    }
    
    const toast = this.createToast(message, type);
    this.container.appendChild(toast);
    this.toasts.push(toast);
    
    // Announce to screen readers
    this.announceToScreenReader(message, type);
    
    // Auto-dismiss after duration (if duration > 0)
    if (duration > 0) {
      const timeoutId = setTimeout(() => {
        this.dismiss(toast);
      }, duration);
      
      // Store timeout ID so we can cancel it if needed
      toast.dataset.timeoutId = timeoutId;
    }
    
    return toast;
  }
  
  /**
   * Create a toast element
   * @param {string} message - The message to display
   * @param {string} type - The type of toast
   * @returns {HTMLElement} The created toast element
   */
  createToast(message, type) {
    const toast = document.createElement('div');
    toast.className = `toast toast--${type}`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    
    // Icon mapping
    const icons = {
      success: '✓',
      error: '✕',
      warning: '⚠',
      info: 'ℹ'
    };
    
    // Title mapping
    const titles = {
      success: 'Success',
      error: 'Error',
      warning: 'Warning',
      info: 'Information'
    };
    
    const icon = icons[type] || 'ℹ';
    const title = titles[type] || 'Notification';
    
    toast.innerHTML = `
      <div class="toast__icon" aria-hidden="true">${icon}</div>
      <div class="toast__content">
        <p class="toast__title">${title}</p>
        <p class="toast__message">${this.escapeHtml(message)}</p>
      </div>
      <button class="toast__close" aria-label="Close notification">&times;</button>
    `;
    
    // Close button handler
    const closeButton = toast.querySelector('.toast__close');
    closeButton.addEventListener('click', () => {
      this.dismiss(toast);
    });
    
    // Add keyboard support for close button
    closeButton.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        this.dismiss(toast);
      }
    });
    
    return toast;
  }
  
  /**
   * Dismiss a toast notification
   * @param {HTMLElement} toast - The toast element to dismiss
   */
  dismiss(toast) {
    if (!toast || !toast.parentElement) {
      return;
    }
    
    // Cancel auto-dismiss timeout if it exists
    if (toast.dataset.timeoutId) {
      clearTimeout(parseInt(toast.dataset.timeoutId));
    }
    
    // Add exit animation
    toast.style.animation = 'slideOut 0.3s ease-out';
    
    // Remove from DOM after animation
    setTimeout(() => {
      if (toast.parentElement) {
        toast.remove();
      }
      this.toasts = this.toasts.filter(t => t !== toast);
    }, 300);
  }
  
  /**
   * Dismiss all toast notifications
   */
  dismissAll() {
    // Create a copy of the array since we'll be modifying it
    const toastsCopy = [...this.toasts];
    toastsCopy.forEach(toast => this.dismiss(toast));
  }
  
  /**
   * Announce message to screen readers
   * @param {string} message - The message to announce
   * @param {string} type - The type of notification
   */
  announceToScreenReader(message, type) {
    const announcement = document.createElement('div');
    announcement.setAttribute('role', 'status');
    announcement.setAttribute('aria-live', 'polite');
    announcement.className = 'sr-only';
    announcement.textContent = `${type}: ${message}`;
    document.body.appendChild(announcement);
    
    // Remove after announcement
    setTimeout(() => {
      announcement.remove();
    }, 1000);
  }
  
  /**
   * Escape HTML to prevent XSS attacks
   * @param {string} text - The text to escape
   * @returns {string} The escaped text
   */
  escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }
}

// Create global toast instance
if (typeof window !== 'undefined') {
  window.toast = new ToastManager();
}

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
  module.exports = ToastManager;
}
