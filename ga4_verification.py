from app import app
import requests
import json
import time
import sys

def verify_ga4_tag():
    """Verify that the Google Analytics 4 tag is correctly implemented on the site."""
    with app.app_context():
        print("Verifying Google Analytics 4 tag implementation...")
        
        # Get the homepage content
        with app.test_client() as client:
            response = client.get('/')
            
            if response.status_code != 200:
                print(f"❌ Error: Could not retrieve homepage (Status code: {response.status_code})")
                return
            
            html_content = response.data.decode('utf-8')
            
            # Check for GA4 tag
            ga4_id = "G-4RLHHRCDK"
            if f"gtag('config', '{ga4_id}')" in html_content:
                print(f"✅ Found Google Analytics 4 tag with Measurement ID: {ga4_id}")
            else:
                print(f"❌ Error: Google Analytics 4 tag with Measurement ID {ga4_id} not found")
                return
            
            # Check for GA4 script
            ga4_script = f'src="https://www.googletagmanager.com/gtag/js?id={ga4_id}"'
            if ga4_script in html_content:
                print(f"✅ Found Google Analytics 4 script tag")
            else:
                print(f"❌ Error: Google Analytics 4 script tag not found")
                return
            
            # Check for enhanced events script
            if 'src="/static/js/ga4-events.js"' in html_content:
                print(f"✅ Found GA4 enhanced events script")
            else:
                print(f"❌ Error: GA4 enhanced events script not found")
            
            print("\nGoogle Analytics 4 verification complete!")
            print("\nNext steps:")
            print("1. Visit your Google Analytics 4 property to confirm data is being collected")
            print("2. It may take up to 24-48 hours for data to appear in your GA4 dashboard")
            print("3. Test custom events by interacting with your site and checking the events report")

if __name__ == "__main__":
    verify_ga4_tag()
