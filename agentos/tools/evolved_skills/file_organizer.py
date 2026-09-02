import os
import shutil

def run(target_dir):
    """
    Organizes files in the target_dir by their extension.
    """
    if not os.path.exists(target_dir):
        return f"Error: Directory {target_dir} does not exist."

    # Extension to Category Mapping
    CATEGORIES = {
        "Images": [".jpg", ".jpeg", ".png", ".gif"],
        "Documents": [".pdf", ".docx", ".txt", ".xlsx", ".pptx"],
        "Media": [".mp4", ".mp3", ".wav", ".mkv"]
    }
    
    # Reverse mapping for fast lookup: extension -> category
    ext_map = {}
    for cat, exts in CATEGORIES.items():
        for ext in exts:
            ext_map[ext] = cat

    organized_count = 0
    for filename in os.listdir(target_dir):
        file_path = os.path.join(target_dir, filename)
        
        # Skip directories
        if os.path.isdir(file_path):
            continue
            
        ext = os.path.splitext(filename)[1].lower()
        category = ext_map.get(ext, "Others")
        
        category_dir = os.path.join(target_dir, category)
        os.makedirs(category_dir, exist_ok=True)
        
        new_path = os.path.join(category_dir, filename)
        shutil.move(file_path, new_path)
        organized_count += 1
        
    return f"Successfully organized {organized_count} files into categories in {target_dir}."
