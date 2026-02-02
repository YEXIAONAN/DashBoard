from django.test import SimpleTestCase
from django.template.loader import get_template


class BaseTemplateRenderingTests(SimpleTestCase):
    """
    Unit tests for base template rendering.
    Tests that design system CSS is loaded, meta tags are present,
    and semantic HTML structure is correct.
    
    Uses SimpleTestCase to avoid database setup since we're only testing template content.
    
    Validates Requirements: 2.1, 11.1
    """
    
    def test_base_template_exists(self):
        """
        Test that base.html template file exists.
        Validates: Requirement 2.1 - Base template creation
        """
        try:
            template = get_template('base.html')
            self.assertIsNotNone(template)
        except Exception as e:
            self.fail(f"base.html template should exist: {e}")
    
    def test_design_system_css_references(self):
        """
        Test that design system CSS files are referenced in the base template.
        Validates: Requirement 2.1 - Design system CSS integration
        """
        template = get_template('base.html')
        template_content = template.template.source
        
        # Check for CSS file references
        self.assertIn('reset.css', template_content, 
                     "reset.css should be referenced in base template")
        self.assertIn('design-system.css', template_content,
                     "design-system.css should be referenced in base template")
        self.assertIn('base-components.css', template_content,
                     "base-components.css should be referenced in base template")
    
    def test_responsive_viewport_meta_tag_in_template(self):
        """
        Test that responsive viewport meta tag is in the template.
        Validates: Requirement 2.1 - Responsive design meta tags
        """
        template = get_template('base.html')
        template_content = template.template.source
        
        self.assertIn('name="viewport"', template_content,
                     "Viewport meta tag should be present")
        self.assertIn('width=device-width', template_content,
                     "Viewport should include width=device-width")
        self.assertIn('initial-scale=1.0', template_content,
                     "Viewport should include initial-scale=1.0")
    
    def test_charset_meta_tag_in_template(self):
        """
        Test that charset meta tag is in the template.
        Validates: Requirement 11.1 - Proper HTML metadata
        """
        template = get_template('base.html')
        template_content = template.template.source
        
        self.assertIn('charset="UTF-8"', template_content,
                     "UTF-8 charset should be specified")
    
    def test_seo_meta_tags_in_template(self):
        """
        Test that SEO meta tags (title, description) are in the template.
        Validates: Requirement 11.1 - SEO metadata
        """
        template = get_template('base.html')
        template_content = template.template.source
        
        # Check for title block
        self.assertIn('<title>', template_content,
                     "Title tag should be present")
        self.assertIn('{% block title %}', template_content,
                     "Title block should be present for page-specific titles")
        
        # Check for meta description
        self.assertIn('name="description"', template_content,
                     "Meta description should be present")
        self.assertIn('{% block meta_description %}', template_content,
                     "Meta description block should be present")
    
    def test_open_graph_meta_tags_in_template(self):
        """
        Test that Open Graph meta tags are in the template for social sharing.
        Validates: Requirement 11.1 - Social media metadata
        """
        template = get_template('base.html')
        template_content = template.template.source
        
        # Check for Open Graph tags
        self.assertIn('property="og:title"', template_content,
                     "og:title should be present")
        self.assertIn('property="og:description"', template_content,
                     "og:description should be present")
        self.assertIn('property="og:type"', template_content,
                     "og:type should be present")
        self.assertIn('property="og:url"', template_content,
                     "og:url should be present")
        self.assertIn('property="og:image"', template_content,
                     "og:image should be present")
    
    def test_semantic_html_structure_in_template(self):
        """
        Test that semantic HTML5 elements are used in the template.
        Validates: Requirement 11.1 - Semantic HTML structure
        """
        template = get_template('base.html')
        template_content = template.template.source
        
        # Check for semantic HTML5 elements
        self.assertIn('<header', template_content,
                     "Header element should be present")
        self.assertIn('<nav', template_content,
                     "Nav element should be present")
        self.assertIn('<main', template_content,
                     "Main element should be present")
        self.assertIn('<footer', template_content,
                     "Footer element should be present")
    
    def test_aria_landmarks_in_template(self):
        """
        Test that ARIA landmarks are in the template for accessibility.
        Validates: Requirement 12.1 - Accessibility landmarks
        """
        template = get_template('base.html')
        template_content = template.template.source
        
        # Check for ARIA roles
        self.assertIn('role="banner"', template_content,
                     "Banner role should be present (header)")
        self.assertIn('role="navigation"', template_content,
                     "Navigation role should be present")
        self.assertIn('role="main"', template_content,
                     "Main role should be present")
        self.assertIn('role="contentinfo"', template_content,
                     "Contentinfo role should be present (footer)")
    
    def test_skip_to_main_content_link_in_template(self):
        """
        Test that skip to main content link is in the template for accessibility.
        Validates: Requirement 12.2 - Keyboard accessibility
        """
        template = get_template('base.html')
        template_content = template.template.source
        
        # Check for skip link
        self.assertIn('skip-link', template_content,
                     "Skip to main content link should be present")
        self.assertIn('#main-content', template_content,
                     "Skip link should target #main-content")
    
    def test_main_content_has_id_in_template(self):
        """
        Test that main content has proper ID for skip link target.
        Validates: Requirement 12.2 - Keyboard accessibility
        """
        template = get_template('base.html')
        template_content = template.template.source
        
        # Check for main content ID
        self.assertIn('id="main-content"', template_content,
                     "Main content should have id='main-content'")
    
    def test_navigation_structure_in_template(self):
        """
        Test that navigation has proper structure and ARIA attributes.
        Validates: Requirement 3.1 - Navigation structure
        """
        template = get_template('base.html')
        template_content = template.template.source
        
        # Check navigation structure
        self.assertIn('class="navbar"', template_content,
                     "Navigation bar should be present")
        
        # Check for aria-label on navigation
        self.assertIn('aria-label', template_content,
                     "Navigation should have aria-label")
        
        # Check for navigation menu
        self.assertIn('navbar__menu', template_content,
                     "Navigation menu should be present")
    
    def test_mobile_menu_toggle_button_in_template(self):
        """
        Test that mobile menu toggle button has proper ARIA attributes.
        Validates: Requirement 3.5 - Mobile navigation
        """
        template = get_template('base.html')
        template_content = template.template.source
        
        # Check for mobile toggle button
        self.assertIn('navbar__toggle', template_content,
                     "Mobile menu toggle should be present")
        
        # Check ARIA attributes
        self.assertIn('aria-label', template_content,
                     "Toggle button should have aria-label")
        self.assertIn('aria-expanded', template_content,
                     "Toggle button should have aria-expanded")
        self.assertIn('aria-controls', template_content,
                     "Toggle button should have aria-controls")
    
    def test_navigation_links_structure(self):
        """
        Test that navigation links structure is present in template.
        Validates: Requirement 3.3 - Navigation links
        """
        template = get_template('base.html')
        template_content = template.template.source
        
        # Check for navigation link structure
        self.assertIn('navbar__link', template_content,
                     "Navigation links should be present")
        self.assertIn('navbar__link--active', template_content,
                     "Active link styling should be present")
        
        # Check for main page links
        self.assertIn("{% url 'index' %}", template_content,
                     "Index page link should be present")
        self.assertIn("{% url 'orders' %}", template_content,
                     "Orders page link should be present")
        self.assertIn("{% url 'profile' %}", template_content,
                     "Profile page link should be present")
    
    def test_footer_structure_in_template(self):
        """
        Test that footer has proper semantic structure.
        Validates: Requirement 11.4 - Semantic HTML
        """
        template = get_template('base.html')
        template_content = template.template.source
        
        # Check footer structure
        self.assertIn('class="site-footer"', template_content,
                     "Footer should be present")
        
        # Check for contentinfo role
        self.assertIn('role="contentinfo"', template_content,
                     "Footer should have contentinfo role")
    
    def test_toast_container_in_template(self):
        """
        Test that toast notification container is in the template.
        Validates: Requirement 15.3 - User feedback system
        """
        template = get_template('base.html')
        template_content = template.template.source
        
        # Check for toast container
        self.assertIn('toast-container', template_content,
                     "Toast container should be present")
        
        # Check ARIA attributes
        self.assertIn('role="region"', template_content,
                     "Toast container should have region role")
        self.assertIn('aria-live="polite"', template_content,
                     "Toast container should have aria-live")
    
    def test_loading_indicator_in_template(self):
        """
        Test that loading indicator is in the base template.
        Validates: Requirement 15.2 - Loading feedback
        """
        template = get_template('base.html')
        template_content = template.template.source
        
        # Check for loading overlay
        self.assertIn('loading-overlay', template_content,
                     "Loading overlay should be present")
        self.assertIn('loading-indicator', template_content,
                     "Loading indicator should be present")
        
        # Check ARIA attributes
        self.assertIn('role="status"', template_content,
                     "Loading indicator should have status role")
    
    def test_csrf_token_helper_function_in_template(self):
        """
        Test that CSRF token helper function is in the template JavaScript.
        Validates: Requirement 6.7 - Form security
        """
        template = get_template('base.html')
        template_content = template.template.source
        
        # Check that getCookie function is in the template
        self.assertIn('function getCookie', template_content,
                     "getCookie function should be present")
        self.assertIn('getCookie(name)', template_content,
                     "getCookie function should accept name parameter")
        self.assertIn('document.cookie', template_content,
                     "Function should access document.cookie for CSRF token")
    
    def test_mobile_navigation_toggle_script_in_template(self):
        """
        Test that mobile navigation toggle JavaScript is in the template.
        Validates: Requirement 3.5 - Mobile navigation functionality
        """
        template = get_template('base.html')
        template_content = template.template.source
        
        # Check for navigation toggle functionality
        self.assertIn('navbar__toggle', template_content,
                     "Toggle button reference should be present")
        self.assertIn('navbar__menu', template_content,
                     "Menu reference should be present")
        self.assertIn('addEventListener', template_content,
                     "Event listeners should be present")
    
    def test_html_lang_attribute_in_template(self):
        """
        Test that HTML element has proper lang attribute.
        Validates: Requirement 12.1 - Accessibility
        """
        template = get_template('base.html')
        template_content = template.template.source
        
        # Check for lang attribute
        self.assertIn('<html lang=', template_content,
                     "HTML should have lang attribute")
    
    def test_favicon_links_in_template(self):
        """
        Test that favicon links are in the template.
        Validates: Requirement 11.1 - Complete metadata
        """
        template = get_template('base.html')
        template_content = template.template.source
        
        # Check for favicon
        self.assertIn('rel="icon"', template_content,
                     "Favicon link should be present")
        
        # Check for apple touch icon
        self.assertIn('rel="apple-touch-icon"', template_content,
                     "Apple touch icon should be present")
    
    def test_font_preload_in_template(self):
        """
        Test that critical fonts are preloaded for performance.
        Validates: Requirement 10.7 - Font loading optimization
        """
        template = get_template('base.html')
        template_content = template.template.source
        
        # Check for font preload
        self.assertIn('rel="preload"', template_content,
                     "Preload links should be present")
    
    def test_robots_meta_tag_in_template(self):
        """
        Test that robots meta tag is in the template for SEO.
        Validates: Requirement 11.7 - SEO optimization
        """
        template = get_template('base.html')
        template_content = template.template.source
        
        # Check for robots meta tag
        self.assertIn('name="robots"', template_content,
                     "Robots meta tag should be present")
    
    def test_content_blocks_present(self):
        """
        Test that template blocks are present for child templates.
        Validates: Requirement 2.1 - Template inheritance structure
        """
        template = get_template('base.html')
        template_content = template.template.source
        
        # Check for essential blocks
        self.assertIn('{% block content %}', template_content,
                     "Content block should be present")
        self.assertIn('{% block extra_css %}', template_content,
                     "Extra CSS block should be present")
        self.assertIn('{% block extra_js %}', template_content,
                     "Extra JS block should be present")
    
    def test_static_file_loading(self):
        """
        Test that Django static file loading is configured.
        Validates: Requirement 2.1 - Static file integration
        """
        template = get_template('base.html')
        template_content = template.template.source
        
        # Check for static file loading
        self.assertIn('{% load static %}', template_content,
                     "Static template tag should be loaded")
        self.assertIn("{% static '", template_content,
                     "Static files should be referenced using static tag")
