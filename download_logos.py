import os
import requests

LOGOS = {
    'aa.png': 'https://www.aa.com/content/images/chrome/rebrand/aa-logo.png',
    'united.png': 'https://www.united.com/ual/en/us/fly/travel/united-logo.png',
    'delta.png': 'https://www.delta.com/content/dam/delta-www/brand-assets/delta-logo.png',
    'southwest.png': 'https://www.southwest.com/assets/images/logos/southwest-airlines-logo.png',
    'air_canada.png': 'https://www.aircanada.com/content/dam/aircanada/common/images/logos/aircanada-logo.png',
    'ba.png': 'https://www.britishairways.com/assets/images/global/logo/ba-logo.png',
    'alaska.png': 'https://www.alaskaair.com/content/images/logos/alaska-airlines-logo.png',
    'jetblue.png': 'https://www.jetblue.com/ui-assets/images/jetblue-logo.png',
    'emirates.png': 'https://c.ekstatic.net/ecl/logos/emirates/emirates-logo.svg',
    'lufthansa.png': 'https://www.lufthansa.com/content/dam/lh/images/local/logos/lufthansa-logo.svg',
    'marriott.png': 'https://www.marriott.com/assets/images/marriott-logo.png',
    'hilton.png': 'https://www.hilton.com/assets/images/hilton-logo.png',
    'ihg.png': 'https://www.ihg.com/content/dam/ihg/images/logos/ihg-logo.png',
    'hyatt.png': 'https://www.hyatt.com/content/dam/hyatt/logos/hyatt-logo.png',
    'wyndham.png': 'https://www.wyndham.com/content/dam/wyndham/logos/wyndham-logo.png',
    'chase.png': 'https://www.chase.com/content/dam/chase-logos/chase-logo.png',
    'amex.png': 'https://www.americanexpress.com/content/dam/amex/us/merchant/supplies-uplift/logos/amex-logo.png',
    'citi.png': 'https://www.citi.com/content/dam/citi/logos/citi-logo.png',
    'capital_one.png': 'https://www.capitalone.com/assets/images/logos/capitalone-logo.png',
    'discover.png': 'https://www.discover.com/content/dam/discover/logos/discover-logo.png'
}

def download_logos():
    logos_dir = os.path.join('static', 'images', 'logos')
    os.makedirs(logos_dir, exist_ok=True)
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    for filename, url in LOGOS.items():
        filepath = os.path.join(logos_dir, filename)
        if not os.path.exists(filepath):
            try:
                response = requests.get(url, headers=headers)
                response.raise_for_status()
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                print(f'Downloaded {filename}')
            except Exception as e:
                print(f'Error downloading {filename}: {e}')
                # Create a placeholder logo with the program name
                create_placeholder_logo(filepath, filename.split('.')[0])

def create_placeholder_logo(filepath, program_name):
    from PIL import Image, ImageDraw, ImageFont
    
    # Create a new image with a white background
    img = Image.new('RGB', (200, 100), color='white')
    d = ImageDraw.Draw(img)
    
    # Use a default font
    try:
        font = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 24)
    except:
        font = ImageFont.load_default()
    
    # Draw the program name
    text = program_name.replace('_', ' ').title()
    bbox = d.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x = (200 - text_width) / 2
    y = (100 - text_height) / 2
    
    d.text((x, y), text, font=font, fill='black')
    img.save(filepath)
    print(f'Created placeholder for {program_name}')

if __name__ == '__main__':
    download_logos()
