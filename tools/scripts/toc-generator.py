import os


def build_toc_recursive(root_dir, level=0):
    """
    Recursively builds the table of contents for the specified directory
    and all its subdirectories at the given level.
    Returns a string containing the table of contents in Markdown format.
    """
    toc = ''
    subdirs = []
    for item in sorted(os.listdir(root_dir)):
        path = os.path.join(root_dir, item)
        if os.path.isdir(path) and item != 'assets':
            sub_toc = build_toc_recursive(path, level+1)
            if sub_toc:
                subdirs.append((item, sub_toc))
            else:
                toc += '{}- [{}]({})\n'.format('  '*level, item, path)
        elif item.endswith('.md') and item != 'README.md':
            title = item[:-3]
            toc += '{}- [{}]({})\n'.format('  '*level, title, path)
    for subdir, sub_toc in sorted(subdirs):
        path = os.path.join(root_dir, subdir)
        toc += '{}- [{}]({})\n'.format('  '*level, subdir, path)
        toc += sub_toc
    return toc


def build_toc(root_dir):
    """
    Recursively builds the table of contents for the specified directory.
    Returns a string containing the table of contents in Markdown format.
    """
    toc = build_toc_recursive(root_dir)
    return toc


# Example usage
toc = build_toc('documents/')
with open('tools/scripts/toc.md', 'w') as f:
    f.write(toc)
