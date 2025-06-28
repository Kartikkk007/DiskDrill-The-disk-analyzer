
import os
import shutil

def get_folder_contents(path):
    contents = []
    try:
        with os.scandir(path) as entries:
            for entry in entries:
                try:
                    size = get_size(entry.path)
                    contents.append({
                        'name': entry.name,
                        'path': entry.path,
                        'size': size,
                        'is_dir': entry.is_dir()
                    })
                except:
                    continue
    except:
        pass
    return contents

def get_size(path):
    total = 0
    if os.path.isfile(path):
        return os.path.getsize(path)
    for dirpath, dirnames, filenames in os.walk(path, topdown=True):
        for f in filenames:
            try:
                total += os.path.getsize(os.path.join(dirpath, f))
            except:
                continue
    return total

def delete_path(path):
    try:
        if os.path.isfile(path):
            os.remove(path)
        elif os.path.isdir(path):
            shutil.rmtree(path)
        return True
    except:
        return False
