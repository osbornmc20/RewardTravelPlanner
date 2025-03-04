import os
import shutil
import datetime

def cleanup_scripts():
    """Move one-off scripts to an archive folder"""
    
    # Create archive directory with timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d")
    archive_dir = f"scripts_archive_{timestamp}"
    
    if not os.path.exists(archive_dir):
        os.makedirs(archive_dir)
        print(f"Created archive directory: {archive_dir}")
    
    # List of scripts to archive
    scripts_to_archive = [
        # Download scripts
        "download_mexico_beach_images.py",
        "download_mexico_hotels_images.py",
        "download_playa_chacala.py",
        "download_playa_tenacatita.py",
        
        # Update scripts
        "update_mexico_beaches_images.py",
        "update_mexico_beaches_with_chacala.py",
        "update_mexico_beaches_with_new_images.py",
        "update_mexico_beaches_with_tenacatita.py",
        "update_mexico_hotels_final.py",
        "update_mexico_hotels_images.py",
        "update_el_ganzo_with_local_images.py",
        "update_header_minimal.py",
        "update_travel_guides_header.py",
        
        # Check and verify scripts
        "check_blog_header.py",
        "check_final_changes.py",
        "check_review_image.py",
        "verify_changes.py",
        
        # Fix scripts
        "fix_image_path.py",
        "fix_mexico_beaches_images.py",
    ]
    
    # Move scripts to archive
    moved_count = 0
    for script in scripts_to_archive:
        if os.path.exists(script):
            shutil.move(script, os.path.join(archive_dir, script))
            print(f"Moved {script} to {archive_dir}")
            moved_count += 1
        else:
            print(f"Script {script} not found, skipping")
    
    print(f"\nArchived {moved_count} scripts to {archive_dir}")
    print("These scripts were used for one-time tasks and have been archived for reference.")
    print(f"If you need them again, you can find them in the {archive_dir} directory.")

if __name__ == "__main__":
    cleanup_scripts()
