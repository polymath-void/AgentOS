import os
import glob

# Paths to exclude
exclude_dirs = ['.git', 'venv', 'venv_safe', 'build', 'dist', '__pycache__', '.pytest_cache']

# Words to replace (Order matters to avoid double replacements)
replacements = {
    'AgentOS': 'ComputeRes',
    'agentos': 'compute_res',
    'AGENTOS': 'COMPUTERES',
    'agentos-core': 'compute-res' # Clean up our temporary change
}

def replace_in_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        return # Skip binary files

    new_content = content
    for old, new in replacements.items():
        new_content = new_content.replace(old, new)
        
    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Updated {filepath}")

for root, dirs, files in os.walk('.'):
    dirs[:] = [d for d in dirs if d not in exclude_dirs and not d.endswith('.egg-info')]
    
    for file in files:
        if file == 'refactor_name.py':
            continue
        filepath = os.path.join(root, file)
        replace_in_file(filepath)

print("File contents updated.")

# Rename the main directory
if os.path.exists('agentos'):
    os.rename('agentos', 'compute_res')
    print("Renamed 'agentos' directory to 'compute_res'")

# Also rename egg-info if it exists
for egg in glob.glob('*.egg-info'):
    import shutil
    shutil.rmtree(egg)
