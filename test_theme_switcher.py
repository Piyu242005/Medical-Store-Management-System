#!/usr/bin/env python3
"""
Test the theme switcher implementation
"""

import sys
from app import app

def test_theme_switcher():
    """Test that theme switcher is properly integrated"""
    
    with app.test_client() as client:
        print("Testing theme switcher implementation...")
        
        # Test 1: Check that base.html loads without errors
        print("\n1. Testing base.html loads...")
        response = client.get('/login')
        assert response.status_code == 200, f"Login page returned {response.status_code}"
        html = response.get_data(as_text=True)
        assert 'theme.js' in html, "theme.js script not found in HTML"
        assert 'setTheme' in html, "setTheme function not found in HTML"
        assert 'Dark + Purple' in html, "Dark + Purple button not found"
        assert 'Dark + Red' in html, "Dark + Red button not found"
        assert 'Light' in html, "Light button not found"
        print("   ✓ base.html contains all theme switcher elements")
        
        # Test 2: Check that theme.js file exists and is accessible
        print("\n2. Testing theme.js is accessible...")
        response = client.get('/static/js/theme.js')
        assert response.status_code == 200, f"theme.js returned {response.status_code}"
        content = response.get_data(as_text=True)
        assert 'setTheme' in content, "setTheme function not in theme.js"
        assert 'applyTheme' in content, "applyTheme function not in theme.js"
        assert 'localStorage' in content, "localStorage not in theme.js"
        print("   ✓ theme.js is accessible and contains required functions")
        
        # Test 3: Check that style.css has CSS variables
        print("\n3. Testing style.css has CSS variables...")
        response = client.get('/static/css/style.css')
        assert response.status_code == 200, f"style.css returned {response.status_code}"
        css = response.get_data(as_text=True)
        assert '--accent' in css, "CSS variable --accent not found"
        assert '--bg-primary' in css, "CSS variable --bg-primary not found"
        assert '--text-primary' in css, "CSS variable --text-primary not found"
        assert 'theme-light' in css, "theme-light class not found in CSS"
        assert 'theme-dark-red' in css, "theme-dark-red class not found in CSS"
        assert 'dark-purple' in css, "dark-purple theme colors not found in CSS"
        print("   ✓ style.css has CSS variables and all theme definitions")
        
        # Test 4: Verify dashboard loads with theme switcher
        print("\n4. Testing authenticated page loads with theme switcher...")
        # First login
        client.post('/login', data={
            'username': 'Piyu',
            'password': 'Piyu24'
        }, follow_redirects=True)
        
        # Check dashboard
        response = client.get('/dashboard')
        assert response.status_code == 200, f"Dashboard returned {response.status_code}"
        html = response.get_data(as_text=True)
        assert 'theme-btn' in html, "theme-btn class not found in dashboard"
        assert 'setTheme' in html, "setTheme function not found in dashboard"
        print("   ✓ Dashboard loads with theme switcher visible")
        
        print("\n✅ All theme switcher tests passed!")
        return True

if __name__ == '__main__':
    try:
        test_theme_switcher()
        sys.exit(0)
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
