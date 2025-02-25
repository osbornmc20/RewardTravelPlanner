from datetime import datetime
from urllib.parse import urljoin

class SitemapGenerator:
    def __init__(self, base_url):
        self.base_url = base_url
        self.urls = []

    def add_url(self, path, priority=0.5, changefreq='weekly'):
        """Add a URL to the sitemap with specified priority and change frequency."""
        self.urls.append({
            'loc': urljoin(self.base_url, path),
            'lastmod': datetime.utcnow().strftime('%Y-%m-%d'),
            'priority': str(priority),
            'changefreq': changefreq
        })

    def generate(self):
        
        xml = ['<?xml version="1.0" encoding="UTF-8"?>']
        xml.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
        
        for url in self.urls:
            xml.append('  <url>')
            xml.append(f'    <loc>{url["loc"]}</loc>')
            xml.append(f'    <lastmod>{url["lastmod"]}</lastmod>')
            xml.append(f'    <changefreq>{url["changefreq"]}</changefreq>')
            xml.append(f'    <priority>{url["priority"]}</priority>')
            xml.append('  </url>')
        
        xml.append('</urlset>')
        return '\n'.join(xml)
