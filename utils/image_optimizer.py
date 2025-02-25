from PIL import Image
import os

def create_thumbnails(directory, size=(300, 300)):
    """Create thumbnails for all jpg images in the directory"""
    for filename in os.listdir(directory):
        if filename.endswith('.jpg') and not filename.endswith('-thumb.jpg'):
            image_path = os.path.join(directory, filename)
            thumb_path = os.path.join(directory, filename.replace('.jpg', '-thumb.jpg'))
            
            # Skip if thumbnail already exists
            if os.path.exists(thumb_path):
                continue
                
            with Image.open(image_path) as img:
                # Calculate new height maintaining aspect ratio
                width = size[0]
                ratio = width / img.size[0]
                height = int(img.size[1] * ratio)
                
                # Create thumbnail
                img.thumbnail((width, height), Image.Resampling.LANCZOS)
                img.save(thumb_path, 'JPEG', quality=80, optimize=True)
