/**
 * Navigation Bar Component JavaScript
 * Handles mobile menu toggle, keyboard navigation, and accessibility features
 */

(function() {
    'use strict';
    
    /**
     * Initialize navigation bar functionality
     */
    function initNavbar() {
        const navToggle = document.querySelector('.navbar__toggle');
        const navMenu = document.querySelector('.navbar__menu');
        
        if (!navToggle || !navMenu) {
            console.warn('Navbar elements not found');
            return;
        }
        
        // Mobile menu toggle
        navToggle.addEventListener('click', function() {
            toggleMobileMenu();
        });
        
        // Close menu when clicking outside
        document.addEventListener('click', function(event) {
            if (!navToggle.contains(event.target) && !navMenu.contains(event.target)) {
                closeMobileMenu();
            }
        });
        
        // Close menu on escape key
        document.addEventListener('keydown', function(event) {
            if (event.key === 'Escape' && navMenu.classList.contains('is-open')) {
                closeMobileMenu();
                navToggle.focus();
            }
        });
        
        // Handle keyboard navigation for menu items
        initKeyboardNavigation();
    }
    
    /**
     * Toggle mobile menu open/closed
     */
    function toggleMobileMenu() {
        const navToggle = document.querySelector('.navbar__toggle');
        const navMenu = document.querySelector('.navbar__menu');
        const isExpanded = navToggle.getAttribute('aria-expanded') === 'true';
        
        navToggle.setAttribute('aria-expanded', !isExpanded);
        navMenu.classList.toggle('is-open');
        document.body.classList.toggle('nav-open');
        
        // Announce to screen readers
        announceToScreenReader(
            !isExpanded ? '导航菜单已打开' : '导航菜单已关闭'
        );
    }
    
    /**
     * Close mobile menu
     */
    function closeMobileMenu() {
        const navToggle = document.querySelector('.navbar__toggle');
        const navMenu = document.querySelector('.navbar__menu');
        
        navToggle.setAttribute('aria-expanded', 'false');
        navMenu.classList.remove('is-open');
        document.body.classList.remove('nav-open');
    }
    
    /**
     * Initialize keyboard navigation for menu items
     */
    function initKeyboardNavigation() {
        const navLinks = document.querySelectorAll('.navbar__link');
        
        navLinks.forEach((link, index) => {
            link.addEventListener('keydown', function(event) {
                // Arrow key navigation
                if (event.key === 'ArrowRight' || event.key === 'ArrowDown') {
                    event.preventDefault();
                    const nextLink = navLinks[index + 1] || navLinks[0];
                    nextLink.focus();
                } else if (event.key === 'ArrowLeft' || event.key === 'ArrowUp') {
                    event.preventDefault();
                    const prevLink = navLinks[index - 1] || navLinks[navLinks.length - 1];
                    prevLink.focus();
                } else if (event.key === 'Home') {
                    event.preventDefault();
                    navLinks[0].focus();
                } else if (event.key === 'End') {
                    event.preventDefault();
                    navLinks[navLinks.length - 1].focus();
                }
            });
        });
    }
    
    /**
     * Announce message to screen readers
     * @param {string} message - Message to announce
     */
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
    
    /**
     * Highlight active page in navigation
     */
    function highlightActivePage() {
        const currentPath = window.location.pathname;
        const navLinks = document.querySelectorAll('.navbar__link');
        
        navLinks.forEach(link => {
            const linkPath = new URL(link.href).pathname;
            
            // Remove active class from all links
            link.classList.remove('navbar__link--active');
            
            // Add active class to matching link
            if (linkPath === currentPath || 
                (currentPath === '/' && linkPath === '/index/')) {
                link.classList.add('navbar__link--active');
                link.setAttribute('aria-current', 'page');
            } else {
                link.removeAttribute('aria-current');
            }
        });
    }
    
    // Initialize on DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            initNavbar();
            highlightActivePage();
        });
    } else {
        initNavbar();
        highlightActivePage();
    }
})();
