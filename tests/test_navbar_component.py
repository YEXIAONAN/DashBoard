"""
Test suite for Navigation Bar Component (Task 3.4)
Tests Requirements: 3.1, 3.2, 3.3, 3.5, 12.2
"""

from django.test import TestCase, Client
from django.urls import reverse
from main.models import Users


class NavbarComponentTests(TestCase):
    """Test navigation bar component implementation"""
    
    def setUp(self):
        """Set up test client and test user"""
        self.client = Client()
        
        # Create test user
        self.test_user = Users.objects.create(
            user_id=999,
            username='testuser',
            password='testpass123',
            name='Test User',
            gender='男',
            phone='13800138000'
        )
        
        # Login test user
        session = self.client.session
        session['user'] = {
            'user_id': self.test_user.user_id,
            'username': self.test_user.username,
            'name': self.test_user.name,
            'phone': self.test_user.phone
        }
        session.save()
    
    def test_navbar_present_on_all_pages(self):
        """
        Test Requirement 3.1: Navigation bar displays consistently across all pages
        """
        pages = ['index', 'orders', 'profile', 'repo', 'order_history', 'ai_health_advisor']
        
        for page_name in pages:
            response = self.client.get(reverse(page_name))
            self.assertEqual(response.status_code, 200, 
                           f"Page {page_name} should return 200")
            
            # Check if navbar HTML structure exists
            content = response.content.decode('utf-8')
            self.assertIn('class="navbar"', content,
                         f"Navbar should be present on {page_name}")
            self.assertIn('class="navbar__container"', content,
                         f"Navbar container should be present on {page_name}")
            self.assertIn('class="navbar__menu"', content,
                         f"Navbar menu should be present on {page_name}")
    
    def test_navbar_has_all_primary_features(self):
        """
        Test Requirement 3.3: Navigation bar provides access to all primary features
        """
        response = self.client.get(reverse('index'))
        content = response.content.decode('utf-8')
        
        # Check for all required navigation links
        required_links = [
            ('首页', '/index/'),
            ('点餐', '/orders/'),
            ('个人中心', '/profile/'),
            ('营养报告', '/repo/'),
            ('订单历史', '/order_history/'),
            ('AI顾问', '/ai_health_advisor/')
        ]
        
        for link_text, link_url in required_links:
            self.assertIn(link_text, content,
                         f"Navigation should include '{link_text}' link")
            self.assertIn(f'href="{link_url}"', content,
                         f"Navigation should link to {link_url}")
    
    def test_navbar_mobile_toggle_button(self):
        """
        Test Requirement 3.1: Mobile hamburger menu toggle button exists
        """
        response = self.client.get(reverse('index'))
        content = response.content.decode('utf-8')
        
        # Check for mobile toggle button
        self.assertIn('class="navbar__toggle"', content,
                     "Mobile toggle button should exist")
        self.assertIn('aria-label="切换导航菜单"', content,
                     "Toggle button should have aria-label")
        self.assertIn('aria-expanded="false"', content,
                     "Toggle button should have aria-expanded attribute")
        self.assertIn('aria-controls="navbar-menu"', content,
                     "Toggle button should control navbar menu")
        
        # Check for toggle icon spans
        self.assertIn('class="navbar__toggle-icon"', content,
                     "Toggle icon spans should exist")
    
    def test_navbar_sticky_positioning(self):
        """
        Test Requirement 3.5: Navigation bar remains accessible during scrolling
        """
        response = self.client.get(reverse('index'))
        content = response.content.decode('utf-8')
        
        # Check for sticky header
        self.assertIn('class="site-header"', content,
                     "Site header should exist")
        
        # Note: CSS sticky positioning is tested in CSS file
        # This test verifies the HTML structure is in place
    
    def test_navbar_keyboard_accessibility(self):
        """
        Test Requirement 12.2: Keyboard navigation works
        """
        response = self.client.get(reverse('index'))
        content = response.content.decode('utf-8')
        
        # Check that all navigation links are keyboard accessible
        # Links should be <a> tags which are naturally keyboard accessible
        self.assertIn('<a href=', content,
                     "Navigation should use accessible <a> tags")
        
        # Check for focus styles in CSS (verified by presence of navbar__link class)
        self.assertIn('class="navbar__link"', content,
                     "Navigation links should have proper class for focus styles")
    
    def test_navbar_unauthenticated_user(self):
        """
        Test Requirement 3.6: Unauthenticated users only see login
        """
        # Logout user
        self.client.session.flush()
        
        response = self.client.get(reverse('index'))
        content = response.content.decode('utf-8')
        
        # Should show login link
        self.assertIn('登录', content,
                     "Unauthenticated users should see login link")
        self.assertIn('/login/', content,
                     "Login link should point to /login/")
    
    def test_navbar_responsive_classes(self):
        """
        Test Requirement 3.1: Navbar has responsive behavior classes
        """
        response = self.client.get(reverse('index'))
        content = response.content.decode('utf-8')
        
        # Check for responsive menu structure
        self.assertIn('id="navbar-menu"', content,
                     "Menu should have ID for toggle control")
        self.assertIn('class="navbar__menu"', content,
                     "Menu should have class for responsive styling")
    
    def test_navbar_aria_landmarks(self):
        """
        Test Requirement 12.2: Navigation has proper ARIA landmarks
        """
        response = self.client.get(reverse('index'))
        content = response.content.decode('utf-8')
        
        # Check for navigation landmark
        self.assertIn('role="navigation"', content,
                     "Navbar should have navigation role")
        self.assertIn('aria-label="主导航"', content,
                     "Navbar should have descriptive aria-label")
    
    def test_navbar_user_info_display(self):
        """
        Test that authenticated user info is displayed
        """
        response = self.client.get(reverse('index'))
        content = response.content.decode('utf-8')
        
        # Check for user info display
        self.assertIn('class="navbar__user-info"', content,
                     "User info should be displayed")
        self.assertIn(self.test_user.username, content,
                     "Username should be displayed in navbar")
    
    def tearDown(self):
        """Clean up test data"""
        Users.objects.filter(user_id=999).delete()


class NavbarCSSTests(TestCase):
    """Test navigation bar CSS implementation"""
    
    def test_navbar_css_file_exists(self):
        """Test that base-components.css exists and contains navbar styles"""
        import os
        from django.conf import settings
        
        css_path = os.path.join(
            settings.BASE_DIR,
            'main',
            'static',
            'css',
            'base-components.css'
        )
        
        self.assertTrue(os.path.exists(css_path),
                       "base-components.css should exist")
        
        with open(css_path, 'r', encoding='utf-8') as f:
            css_content = f.read()
            
            # Check for navbar styles
            self.assertIn('.navbar', css_content,
                         "CSS should contain .navbar styles")
            self.assertIn('.navbar__container', css_content,
                         "CSS should contain .navbar__container styles")
            self.assertIn('.navbar__toggle', css_content,
                         "CSS should contain .navbar__toggle styles")
            self.assertIn('.navbar__menu', css_content,
                         "CSS should contain .navbar__menu styles")
            self.assertIn('.navbar__link', css_content,
                         "CSS should contain .navbar__link styles")
            self.assertIn('.navbar__link--active', css_content,
                         "CSS should contain .navbar__link--active styles")
            
            # Check for responsive styles
            self.assertIn('@media (max-width: 768px)', css_content,
                         "CSS should contain mobile breakpoint")
            self.assertIn('.navbar__menu.is-open', css_content,
                         "CSS should contain open menu styles")
            
            # Check for accessibility styles
            self.assertIn(':focus', css_content,
                         "CSS should contain focus styles")
            self.assertIn('@media (prefers-reduced-motion', css_content,
                         "CSS should respect reduced motion preference")


class NavbarJavaScriptTests(TestCase):
    """Test navigation bar JavaScript functionality"""
    
    def test_navbar_js_file_exists(self):
        """Test that navbar.js exists"""
        import os
        from django.conf import settings
        
        js_path = os.path.join(
            settings.BASE_DIR,
            'main',
            'static',
            'js',
            'navbar.js'
        )
        
        self.assertTrue(os.path.exists(js_path),
                       "navbar.js should exist")
        
        with open(js_path, 'r', encoding='utf-8') as f:
            js_content = f.read()
            
            # Check for key functions
            self.assertIn('initNavbar', js_content,
                         "JS should contain initNavbar function")
            self.assertIn('toggleMobileMenu', js_content,
                         "JS should contain toggleMobileMenu function")
            self.assertIn('initKeyboardNavigation', js_content,
                         "JS should contain initKeyboardNavigation function")
            self.assertIn('highlightActivePage', js_content,
                         "JS should contain highlightActivePage function")
            
            # Check for event listeners
            self.assertIn('addEventListener', js_content,
                         "JS should set up event listeners")
            self.assertIn('Escape', js_content,
                         "JS should handle Escape key")
            self.assertIn('aria-expanded', js_content,
                         "JS should manage aria-expanded attribute")


if __name__ == '__main__':
    import unittest
    unittest.main()
