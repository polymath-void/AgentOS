"""\nSkill: media_perceptual_dedup\nCategory: media-management\nDescription: Safe redesign of HoloDedup: Computes dhash for images to find visually similar files and optionally hardlinks them.\n"""\n\ndef run(**kwargs):
    import os
    try:
        from PIL import Image
    except ImportError:
        return {'error': 'Pillow library required: pip install Pillow'}
    directory = kwargs.get('directory', '.')
    dry_run = kwargs.get('dry_run', True)
    
    def dhash(image, hash_size=8):
        image = image.convert('L').resize((hash_size + 1, hash_size), Image.Resampling.LANCZOS)
        pixels = list(image.getdata())
        diff = [pixels[row*hash_size + col] > pixels[row*hash_size + col + 1] for row in range(hash_size) for col in range(hash_size)]
        return sum([2 ** i for (i, v) in enumerate(diff) if v])
        
    hashes = {}; duplicates = []
    for root, _, files in os.walk(directory):
        for f in files:
            if not f.lower().endswith(('.png', '.jpg', '.jpeg')): continue
            path = os.path.join(root, f)
            try:
                with Image.open(path) as img: h = dhash(img)
                if h in hashes:
                    orig = hashes[h]
                    duplicates.append((path, orig))
                    if not dry_run:
                        os.remove(path); os.link(orig, path)
                else: hashes[h] = path
            except Exception: pass
    return {'status': 'completed', 'duplicates_found': len(duplicates), 'dry_run': dry_run}
