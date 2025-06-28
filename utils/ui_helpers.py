#importing the  file size in bytes functionality and filter functionality to the gui file
def format_size(size_bytes):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} PB"

def filter_items_by_name(items, query):
    query = query.lower()
    return [item for item in items if query in item['name'].lower()]
