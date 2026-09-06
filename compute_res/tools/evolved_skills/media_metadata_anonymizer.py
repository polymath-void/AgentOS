"""\nSkill: media_metadata_anonymizer\nCategory: media-management\nDescription: Safe redesign of ChronoScrubber: Strips EXIF metadata from images in a folder without intercepting system writes.\n"""\n\ndef run(**kwargs):
    import os
    try:
        from PIL import Image
    except ImportError:
        return {'error': 'Pillow library required: pip install Pillow'}
    directory = kwargs.get('directory', '.')
    processed = 0
    for root, _, files in os.walk(directory):
        for f in files:
            if not f.lower().endswith(('.png', '.jpg', '.jpeg')): continue
            path = os.path.join(root, f)
            try:
                with Image.open(path) as img:
                    data = list(img.getdata())
                    clean = Image.new(img.mode, img.size)
                    clean.putdata(data)
                    clean.save(path)
                processed += 1
            except Exception: pass
    return {'status': 'completed', 'images_anonymized': processed}
