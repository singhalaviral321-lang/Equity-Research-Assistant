import os
import shutil
import glob

def rescue_reports():
    # 1. Define target directory relative to this script
    base_dir = os.path.dirname(os.path.abspath(__file__))
    target_dir = os.path.join(base_dir, "reports")
    
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
        print(f"📁 Created directory: {target_dir}")

    # 2. Define search locations
    # a) Current directory
    # b) One level up
    # c) Desktop (Windows)
    desktop = os.path.join(os.path.expanduser("~"), "Desktop")
    
    search_patterns = [
        os.path.join(os.getcwd(), "analysis_*.json"),
        os.path.join(os.path.dirname(os.getcwd()), "analysis_*.json"),
        os.path.join(desktop, "analysis_*.json"),
        os.path.join(base_dir, "analysis_*.json")
    ]

    moved_count = 0
    
    print("🔍 Searching for orphaned analysis reports...")
    
    found_files = []
    for pattern in search_patterns:
        found_files.extend(glob.glob(pattern))
    
    # Remove duplicates if any
    found_files = list(set(found_files))

    for file_path in found_files:
        filename = os.path.basename(file_path)
        dest_path = os.path.join(target_dir, filename)
        
        # Don't move if it's already in the target dir
        if os.path.abspath(file_path) == os.path.abspath(dest_path):
            continue
            
        try:
            shutil.move(file_path, dest_path)
            print(f"✅ MOVED: {filename}")
            print(f"   FROM: {file_path}")
            print(f"   TO:   {dest_path}")
            moved_count += 1
        except Exception as e:
            print(f"❌ Failed to move {filename}: {e}")

    if moved_count == 0:
        print("🤷 No orphaned reports found in common locations.")
    else:
        print(f"\n🎉 Successfully rescued {moved_count} report(s).")

if __name__ == "__main__":
    rescue_reports()
