from app import app
from models.review import Review
import xml.etree.ElementTree as ET
import requests

def verify_sitemap():
    """Verify that the sitemap includes all necessary URLs and is properly formatted."""
    with app.app_context():
        print("Verifying sitemap.xml...")
        
        # Get the sitemap content
        with app.test_client() as client:
            response = client.get('/sitemap.xml')
            
            if response.status_code != 200:
                print(f"❌ Error: Could not retrieve sitemap.xml (Status code: {response.status_code})")
                return
            
            sitemap_content = response.data.decode('utf-8')
            
            # Parse the XML
            try:
                root = ET.fromstring(sitemap_content)
                
                # Count URLs
                urls = root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}url')
                print(f"✅ Found {len(urls)} URLs in sitemap")
                
                # Check for main pages
                main_pages = ['/travel-guides', '/hotel-rankings']
                for page in main_pages:
                    if not any(page in url.find('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc').text for url in urls):
                        print(f"❌ Missing main page: {page}")
                    else:
                        print(f"✅ Found main page: {page}")
                
                # Check for reviews
                reviews = Review.get_all_published()
                for review in reviews:
                    review_url = f"/reviews/{review.slug}"
                    if not any(review_url in url.find('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc').text for url in urls):
                        print(f"❌ Missing review: {review_url}")
                    else:
                        print(f"✅ Found review: {review_url}")
                
                print("\nSitemap verification complete!")
                
            except ET.ParseError as e:
                print(f"❌ Error: Invalid XML in sitemap: {str(e)}")
                return

if __name__ == "__main__":
    verify_sitemap()
