#!/usr/bin/env python3
"""
Mobile Compatibility Test Script for QuXAT Scoring Application

This script tests various mobile compatibility features and responsive design elements
to ensure the application works well on mobile and tablet devices.
"""

import requests
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json

class MobileCompatibilityTester:
    def __init__(self, base_url="http://localhost:8501"):
        self.base_url = base_url
        self.test_results = {
            "viewport_test": False,
            "responsive_layout": False,
            "touch_targets": False,
            "mobile_navigation": False,
            "font_sizes": False,
            "button_accessibility": False,
            "form_usability": False,
            "overall_score": 0
        }
        
    def setup_mobile_driver(self, device_type="mobile"):
        """Setup Chrome driver with mobile device emulation"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        # Device configurations
        devices = {
            "mobile": {
                "deviceMetrics": {"width": 375, "height": 667, "pixelRatio": 2.0},
                "userAgent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15"
            },
            "tablet": {
                "deviceMetrics": {"width": 768, "height": 1024, "pixelRatio": 2.0},
                "userAgent": "Mozilla/5.0 (iPad; CPU OS 14_0 like Mac OS X) AppleWebKit/605.1.15"
            },
            "small_mobile": {
                "deviceMetrics": {"width": 320, "height": 568, "pixelRatio": 2.0},
                "userAgent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15"
            }
        }
        
        device_config = devices.get(device_type, devices["mobile"])
        chrome_options.add_experimental_option("mobileEmulation", device_config)
        
        try:
            driver = webdriver.Chrome(options=chrome_options)
            return driver
        except Exception as e:
            print(f"⚠️ Could not setup Chrome driver: {e}")
            print("📱 Continuing with basic connectivity tests...")
            return None
    
    def test_basic_connectivity(self):
        """Test if the Streamlit app is accessible"""
        try:
            response = requests.get(self.base_url, timeout=10)
            if response.status_code == 200:
                print("✅ Streamlit app is accessible")
                return True
            else:
                print(f"❌ App returned status code: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Could not connect to app: {e}")
            return False
    
    def test_viewport_configuration(self, driver):
        """Test viewport meta tag and responsive configuration"""
        try:
            driver.get(self.base_url)
            time.sleep(3)
            
            # Check if viewport meta tag exists
            viewport_meta = driver.find_elements(By.XPATH, "//meta[@name='viewport']")
            
            if viewport_meta:
                viewport_content = viewport_meta[0].get_attribute("content")
                print(f"✅ Viewport meta tag found: {viewport_content}")
                
                # Check for mobile-friendly viewport settings
                mobile_friendly_keywords = ["width=device-width", "initial-scale=1"]
                has_mobile_settings = all(keyword in viewport_content for keyword in mobile_friendly_keywords)
                
                if has_mobile_settings:
                    print("✅ Mobile-friendly viewport configuration detected")
                    self.test_results["viewport_test"] = True
                    return True
                else:
                    print("⚠️ Viewport configuration may not be optimal for mobile")
                    return False
            else:
                print("❌ No viewport meta tag found")
                return False
                
        except Exception as e:
            print(f"❌ Viewport test failed: {e}")
            return False
    
    def test_responsive_layout(self, driver):
        """Test responsive layout behavior"""
        try:
            driver.get(self.base_url)
            time.sleep(3)
            
            # Test different screen sizes
            screen_sizes = [
                (375, 667),  # iPhone
                (768, 1024), # iPad
                (320, 568),  # Small mobile
            ]
            
            layout_responsive = True
            
            for width, height in screen_sizes:
                driver.set_window_size(width, height)
                time.sleep(2)
                
                # Check if content is visible and not overflowing
                body = driver.find_element(By.TAG_NAME, "body")
                body_width = body.size['width']
                
                if body_width > width + 50:  # Allow some tolerance
                    print(f"⚠️ Content may be overflowing at {width}x{height}")
                    layout_responsive = False
                else:
                    print(f"✅ Layout looks good at {width}x{height}")
            
            self.test_results["responsive_layout"] = layout_responsive
            return layout_responsive
            
        except Exception as e:
            print(f"❌ Responsive layout test failed: {e}")
            return False
    
    def test_touch_targets(self, driver):
        """Test if interactive elements meet touch target size requirements"""
        try:
            driver.get(self.base_url)
            time.sleep(3)
            
            # Find buttons and check their size
            buttons = driver.find_elements(By.CSS_SELECTOR, "button")
            touch_friendly_count = 0
            total_buttons = len(buttons)
            
            min_touch_size = 44  # Apple's recommendation
            
            for button in buttons:
                if button.is_displayed():
                    size = button.size
                    if size['height'] >= min_touch_size and size['width'] >= min_touch_size:
                        touch_friendly_count += 1
            
            if total_buttons > 0:
                touch_friendly_ratio = touch_friendly_count / total_buttons
                print(f"✅ {touch_friendly_count}/{total_buttons} buttons meet touch target requirements")
                
                if touch_friendly_ratio >= 0.8:  # 80% of buttons should be touch-friendly
                    self.test_results["touch_targets"] = True
                    return True
                else:
                    print("⚠️ Some buttons may be too small for touch interaction")
                    return False
            else:
                print("⚠️ No buttons found to test")
                return False
                
        except Exception as e:
            print(f"❌ Touch targets test failed: {e}")
            return False
    
    def test_font_readability(self, driver):
        """Test font sizes for mobile readability"""
        try:
            driver.get(self.base_url)
            time.sleep(3)
            
            # Set mobile viewport
            driver.set_window_size(375, 667)
            time.sleep(2)
            
            # Check various text elements
            text_elements = driver.find_elements(By.CSS_SELECTOR, "p, span, div, h1, h2, h3, h4, h5, h6")
            readable_count = 0
            total_elements = 0
            
            min_font_size = 14  # Minimum readable font size on mobile
            
            for element in text_elements:
                if element.is_displayed() and element.text.strip():
                    font_size = driver.execute_script(
                        "return window.getComputedStyle(arguments[0]).fontSize;", element
                    )
                    
                    if font_size:
                        size_px = float(font_size.replace('px', ''))
                        total_elements += 1
                        
                        if size_px >= min_font_size:
                            readable_count += 1
            
            if total_elements > 0:
                readability_ratio = readable_count / total_elements
                print(f"✅ {readable_count}/{total_elements} text elements have readable font sizes")
                
                if readability_ratio >= 0.9:  # 90% should be readable
                    self.test_results["font_sizes"] = True
                    return True
                else:
                    print("⚠️ Some text may be too small for mobile reading")
                    return False
            else:
                print("⚠️ No text elements found to test")
                return False
                
        except Exception as e:
            print(f"❌ Font readability test failed: {e}")
            return False
    
    def run_comprehensive_test(self):
        """Run all mobile compatibility tests"""
        print("🚀 Starting Mobile Compatibility Test for QuXAT Scoring Application")
        print("=" * 70)
        
        # Test basic connectivity first
        if not self.test_basic_connectivity():
            print("❌ Cannot proceed with tests - app is not accessible")
            return self.test_results
        
        # Test with different device types
        device_types = ["mobile", "tablet", "small_mobile"]
        
        for device_type in device_types:
            print(f"\n📱 Testing {device_type.upper()} compatibility...")
            print("-" * 50)
            
            driver = self.setup_mobile_driver(device_type)
            
            if driver:
                try:
                    # Run tests
                    self.test_viewport_configuration(driver)
                    self.test_responsive_layout(driver)
                    self.test_touch_targets(driver)
                    self.test_font_readability(driver)
                    
                finally:
                    driver.quit()
            else:
                print(f"⚠️ Skipping browser tests for {device_type}")
        
        # Calculate overall score
        passed_tests = sum(1 for result in self.test_results.values() if result is True)
        total_tests = len([k for k in self.test_results.keys() if k != "overall_score"])
        self.test_results["overall_score"] = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        return self.test_results
    
    def print_results(self):
        """Print comprehensive test results"""
        print("\n" + "=" * 70)
        print("📊 MOBILE COMPATIBILITY TEST RESULTS")
        print("=" * 70)
        
        test_descriptions = {
            "viewport_test": "Viewport Meta Tag Configuration",
            "responsive_layout": "Responsive Layout Behavior",
            "touch_targets": "Touch Target Size Requirements",
            "mobile_navigation": "Mobile Navigation Usability",
            "font_sizes": "Font Size Readability",
            "button_accessibility": "Button Accessibility",
            "form_usability": "Form Element Usability"
        }
        
        for test_key, description in test_descriptions.items():
            if test_key in self.test_results:
                status = "✅ PASS" if self.test_results[test_key] else "❌ FAIL"
                print(f"{description:<35} {status}")
        
        print("-" * 70)
        print(f"Overall Mobile Compatibility Score: {self.test_results['overall_score']:.1f}%")
        
        if self.test_results['overall_score'] >= 80:
            print("🎉 Excellent mobile compatibility!")
        elif self.test_results['overall_score'] >= 60:
            print("👍 Good mobile compatibility with room for improvement")
        else:
            print("⚠️ Mobile compatibility needs significant improvement")
        
        print("=" * 70)

def main():
    """Main function to run mobile compatibility tests"""
    tester = MobileCompatibilityTester()
    
    try:
        results = tester.run_comprehensive_test()
        tester.print_results()
        
        # Save results to file
        with open('mobile_compatibility_results.json', 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n📄 Detailed results saved to: mobile_compatibility_results.json")
        
        return results['overall_score'] >= 70  # Return True if tests mostly pass
        
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)