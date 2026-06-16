import os


def get_dir_size(path="."):
    total = 0
    with os.scandir(path) as it:
        for entry in it:
            if entry.is_file():
                total += entry.stat().st_size
            elif entry.is_dir():
                total += get_dir_size(entry.path)
    return total


def format_size(num_bytes):
    KB = 1024
    MB = KB * 1024
    GB = MB * 1024

    if num_bytes >= GB:
        return f"{num_bytes / GB:.2f} GB"
    elif num_bytes >= MB:
        return f"{num_bytes / MB:.2f} MB"
    elif num_bytes >= KB:
        return f"{num_bytes / KB:.2f} KB"
    else:
        return f"{num_bytes} bytes"
