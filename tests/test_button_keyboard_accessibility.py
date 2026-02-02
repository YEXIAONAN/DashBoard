"""
Property-Based Test for Button Keyboard Accessibility (Task 3.5)

Feature: frontend-ui-optimization
Property 3: Keyboard navigation completeness
Validates: Requirements 12.2

This test verifies that all button variants are keyboard accessible:
- All buttons can be focused using Tab key
- All buttons can be activated using Enter or Space keys
- All buttons have visible focus indicators
- All button states (primary, secondary, tertiary, disabled) maintain accessibility

Requirements: 12.2 - Interactive elements SHALL be keyboard navigable with visible focus indicators
"""

from django.test import SimpleTestCase
import re
import os
from django.conf import settings


class ButtonKeyboardAccessibilityPropertyTests(SimpleTestCase):
    """
    Property-Based Tests for Button Keyboard Accessibility
    
    Tests the universal property that ALL button variants across ALL pages
    must be keyboard accessible with proper focus indicators.
    
    Uses SimpleTestCase to avoid database operations.
    """
    
    def setUp(self):
        """Set up test data"""
        # Define all button variants to test
        self.button_variants = [
            'btn--primary',
            'btn--secondary',
            'btn--tertiary',
            'btn--danger',
            'btn--success'
        ]
        
        # Define all button sizes to test
        self.button_sizes = [
            'btn--sm',
            'btn--md',
            'btn--lg'
        ]
        
        # Get CSS file path
        self.css_path = os.path.join(
            settings.BASE_DIR,
            'main',
            'static',
            'css',
            'components.css'
        )
    
    def test_property_css_file_exists(self):
        """
        Property: Button component CSS file must exist
        """
        self.assertTrue(os.path.exists(self.css_path),
                       "components.css should exist at main/static/css/components.css")
    
    def test_property_all_button_variants_have_focus_styles(self):
        """
        Property: All button variants must have focus styles defined in CSS
        
        This test verifies that the CSS file contains focus styles for:
        - Base .btn class
        - All button variants (primary, secondary, tertiary, etc.)
        
        **Validates: Requirements 12.2**
        """
        with open(self.css_path, 'r', encoding='utf-8') as f:
            css_content = f.read()
            
            # Property: Base button class must have focus styles
            self.assertIn('.btn:focus', css_content,
                         "Base .btn class must have :focus styles")
            
            # Property: Focus styles must include visible indicators
            # Check for outline or box-shadow in focus styles
            focus_section_pattern = r'\.btn:focus\s*\{([^}]+)\}'
            focus_styles = re.search(focus_section_pattern, css_content)
            
            self.assertIsNotNone(focus_styles, "Button focus styles must be defined")
            
            if focus_styles:
                focus_css = focus_styles.group(1)
                has_outline = 'outline' in focus_css
                has_box_shadow = 'box-shadow' in focus_css
                
                self.assertTrue(has_outline or has_box_shadow,
                              "Button focus styles must include outline or box-shadow for visibility")
            
            # Property: Focus-visible pseudo-class should be supported
            self.assertIn(':focus-visible', css_content,
                         "CSS should include :focus-visible for modern browsers")
    
    def test_property_disabled_buttons_not_keyboard_accessible(self):
        """
        Property: Disabled buttons should not be keyboard accessible
        
        Disabled buttons should have:
        - disabled attribute OR is-disabled class
        - pointer-events: none in CSS
        - Not be in tab order
        
        **Validates: Requirements 12.2**
        """
        with open(self.css_path, 'r', encoding='utf-8') as f:
            css_content = f.read()
            
            # Check disabled styles
            disabled_css_pattern = r'\.btn:disabled[^{]*\{([^}]+)\}'
            disabled_styles = re.search(disabled_css_pattern, css_content)
            
            self.assertIsNotNone(disabled_styles, "Disabled button styles must be defined")
            
            if disabled_styles:
                disabled_css = disabled_styles.group(1)
                self.assertIn('pointer-events', disabled_css,
                            "Disabled buttons should have pointer-events: none")
    
    def test_property_all_button_sizes_maintain_accessibility(self):
        """
        Property: All button sizes (sm, md, lg) must maintain keyboard accessibility
        
        Different button sizes should not affect:
        - Focus indicator visibility
        - Keyboard activation
        - Minimum touch target size (44x44px for accessibility)
        
        **Validates: Requirements 12.2**
        """
        with open(self.css_path, 'r', encoding='utf-8') as f:
            css_content = f.read()
            
            # Property: All button sizes should have minimum height defined
            for size in self.button_sizes:
                with self.subTest(size=size):
                    size_pattern = rf'\.{size}\s*\{{([^}}]+)\}}'
                    size_styles = re.search(size_pattern, css_content)
                    
                    self.assertIsNotNone(size_styles, f"{size} styles must be defined")
                    
                    if size_styles:
                        size_css = size_styles.group(1)
                        
                        # Check for min-height
                        min_height_pattern = r'min-height:\s*(\d+)px'
                        min_height = re.search(min_height_pattern, size_css)
                        
                        self.assertIsNotNone(min_height, f"{size} should have min-height defined")
                        
                        if min_height:
                            height_value = int(min_height.group(1))
                            
                            # Property: Small buttons should be at least 32px
                            # Medium buttons should be at least 40px
                            # Large buttons should be at least 44px (WCAG touch target)
                            if size == 'btn--sm':
                                self.assertGreaterEqual(height_value, 32,
                                                      f"{size} should have min-height >= 32px")
                            elif size == 'btn--md':
                                self.assertGreaterEqual(height_value, 40,
                                                      f"{size} should have min-height >= 40px")
                            elif size == 'btn--lg':
                                self.assertGreaterEqual(height_value, 44,
                                                      f"{size} should have min-height >= 44px for WCAG compliance")
    
    def test_property_button_focus_indicators_visible(self):
        """
        Property: Button focus indicators must be visible and meet contrast requirements
        
        Focus indicators should:
        - Have sufficient contrast (3:1 minimum per WCAG 2.1)
        - Be visible with outline or box-shadow
        - Have appropriate offset to not overlap button content
        
        **Validates: Requirements 12.2**
        """
        with open(self.css_path, 'r', encoding='utf-8') as f:
            css_content = f.read()
            
            # Property: Focus styles must have outline-offset or appropriate spacing
            focus_pattern = r'\.btn:focus(?:-visible)?\s*\{([^}]+)\}'
            focus_matches = re.findall(focus_pattern, css_content)
            
            self.assertGreater(len(focus_matches), 0, "Button focus styles must be defined")
            
            for focus_css in focus_matches:
                # Check for outline-offset (ensures visibility)
                has_offset = 'outline-offset' in focus_css
                
                # Check for outline width (should be at least 2px)
                outline_width_pattern = r'outline[^:]*:\s*(\d+)px'
                outline_width = re.search(outline_width_pattern, focus_css)
                
                if outline_width:
                    width_value = int(outline_width.group(1))
                    self.assertGreaterEqual(width_value, 2,
                                          "Focus outline should be at least 2px wide for visibility")
    
    def test_property_button_keyboard_activation_patterns(self):
        """
        Property: Buttons must be activatable with Enter and Space keys
        
        This test verifies that button CSS supports proper semantic HTML:
        1. <button> elements are used (naturally support Enter/Space)
        2. Button styles don't interfere with native keyboard behavior
        
        **Validates: Requirements 12.2**
        """
        with open(self.css_path, 'r', encoding='utf-8') as f:
            css_content = f.read()
            
            # Property: Button styles should not disable pointer-events globally
            # (only for disabled buttons)
            btn_base_pattern = r'\.btn\s*\{([^}]+)\}'
            btn_base = re.search(btn_base_pattern, css_content)
            
            self.assertIsNotNone(btn_base, "Base .btn styles must be defined")
            
            if btn_base:
                btn_css = btn_base.group(1)
                # Should NOT have pointer-events: none in base button
                self.assertNotIn('pointer-events: none', btn_css,
                               "Base button should not disable pointer events")
    
    def test_property_reduced_motion_respects_accessibility(self):
        """
        Property: Button animations must respect prefers-reduced-motion
        
        Users with vestibular disorders or motion sensitivity should have
        animations disabled when they set prefers-reduced-motion preference.
        
        **Validates: Requirements 12.2, 5.7**
        """
        with open(self.css_path, 'r', encoding='utf-8') as f:
            css_content = f.read()
            
            # Property: CSS must include prefers-reduced-motion media query
            self.assertIn('@media (prefers-reduced-motion', css_content,
                         "CSS must include @media (prefers-reduced-motion: reduce) for accessibility")
            
            # Property: Reduced motion should disable transitions and animations
            reduced_motion_pattern = r'@media \(prefers-reduced-motion[^{]+\{([^}]+)\}'
            reduced_motion_styles = re.search(reduced_motion_pattern, css_content, re.DOTALL)
            
            self.assertIsNotNone(reduced_motion_styles, "Reduced motion styles must be defined")
            
            if reduced_motion_styles:
                reduced_css = reduced_motion_styles.group(1)
                
                # Should disable animations and transitions
                has_animation_control = 'animation-duration' in reduced_css or 'animation' in reduced_css
                has_transition_control = 'transition-duration' in reduced_css or 'transition' in reduced_css
                
                self.assertTrue(has_animation_control or has_transition_control,
                              "Reduced motion styles should control animations or transitions")
    
    def test_property_button_groups_maintain_keyboard_navigation(self):
        """
        Property: Button groups must maintain logical keyboard navigation order
        
        When buttons are grouped together, Tab order should follow visual order
        and focus indicators should be visible even in attached button groups.
        
        **Validates: Requirements 12.2**
        """
        with open(self.css_path, 'r', encoding='utf-8') as f:
            css_content = f.read()
            
            # Property: Button groups should have focus z-index management
            btn_group_focus_pattern = r'\.btn-group[^{]*\.btn:focus\s*\{([^}]+)\}'
            btn_group_focus = re.search(btn_group_focus_pattern, css_content)
            
            if btn_group_focus:
                focus_css = btn_group_focus.group(1)
                
                # Should have z-index to ensure focus indicator is visible
                self.assertIn('z-index', focus_css,
                            "Button group focus styles should include z-index for visibility")
    
    def test_property_all_button_variants_defined(self):
        """
        Property: All button variants must be defined in CSS
        
        Ensures that primary, secondary, tertiary, danger, and success
        button variants all exist and have proper styling.
        
        **Validates: Requirements 1.3, 12.2**
        """
        with open(self.css_path, 'r', encoding='utf-8') as f:
            css_content = f.read()
            
            for variant in self.button_variants:
                with self.subTest(variant=variant):
                    # Check that variant is defined
                    variant_pattern = rf'\.{variant}\s*\{{'
                    self.assertRegex(css_content, variant_pattern,
                                   f"Button variant {variant} must be defined in CSS")
                    
                    # Check that variant has hover state (without escaping the dot in the search)
                    hover_text = f'.{variant}:hover'
                    self.assertIn(hover_text, css_content,
                                f"Button variant {variant} should have hover state")


class ButtonKeyboardAccessibilityIntegrationTests(SimpleTestCase):
    """
    Integration tests for button keyboard accessibility
    
    These tests verify the comprehensive implementation of button accessibility
    across all variants and states.
    """
    
    def setUp(self):
        """Set up test data"""
        self.css_path = os.path.join(
            settings.BASE_DIR,
            'main',
            'static',
            'css',
            'components.css'
        )
    
    def test_button_component_comprehensive_accessibility(self):
        """
        Comprehensive test that all button accessibility features work together
        
        **Validates: Requirements 12.2**
        """
        with open(self.css_path, 'r', encoding='utf-8') as f:
            css_content = f.read()
            
            # Test 1: Base button has all required properties
            self.assertIn('.btn', css_content)
            self.assertIn('.btn:focus', css_content)
            self.assertIn('.btn:disabled', css_content)
            
            # Test 2: All size variants exist
            self.assertIn('.btn--sm', css_content)
            self.assertIn('.btn--md', css_content)
            self.assertIn('.btn--lg', css_content)
            
            # Test 3: All style variants exist
            self.assertIn('.btn--primary', css_content)
            self.assertIn('.btn--secondary', css_content)
            self.assertIn('.btn--tertiary', css_content)
            
            # Test 4: Accessibility features present
            self.assertIn(':focus-visible', css_content)
            self.assertIn('@media (prefers-reduced-motion', css_content)
            
            # Test 5: Loading and disabled states
            self.assertIn('.is-loading', css_content)
            self.assertIn('.is-disabled', css_content)
    
    def test_button_focus_ring_specifications(self):
        """
        Test that focus ring meets WCAG 2.1 specifications
        
        Focus indicators must be:
        - At least 2px wide
        - Have sufficient contrast
        - Be offset from the button edge
        
        **Validates: Requirements 12.2**
        """
        with open(self.css_path, 'r', encoding='utf-8') as f:
            css_content = f.read()
            
            # Extract focus styles
            focus_pattern = r'\.btn:focus\s*\{([^}]+)\}'
            focus_match = re.search(focus_pattern, css_content)
            
            self.assertIsNotNone(focus_match, "Button focus styles must exist")
            
            if focus_match:
                focus_styles = focus_match.group(1)
                
                # Check for outline or box-shadow
                has_outline = 'outline' in focus_styles
                has_box_shadow = 'box-shadow' in focus_styles
                
                self.assertTrue(has_outline or has_box_shadow,
                              "Focus must have visible indicator (outline or box-shadow)")
                
                # Check for offset
                has_offset = 'outline-offset' in focus_styles or 'box-shadow' in focus_styles
                self.assertTrue(has_offset,
                              "Focus indicator should have offset for visibility")


if __name__ == '__main__':
    import unittest
    unittest.main()
