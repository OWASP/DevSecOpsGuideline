"""Build the home page from the repository README.md and an "About" page from current-version/README.md.

The sidebar already lists every topic, so the Table of Contents sections are dropped.
The "Contributing" section of the root README becomes its own page.
"""

import os
import re

from mkdocs.structure.files import File

REPO = "https://github.com/OWASP/DevSecOpsGuideline"


def _sections(text):
    """Split markdown into (heading, body) chunks on level-2 headings; heading is '' for the preamble."""
    parts = re.split(r"(?m)^(?=## )", text)
    out = []
    for part in parts:
        heading = part.split("\n", 1)[0] if part.startswith("## ") else ""
        out.append((heading, part))
    return out


def _drop(text, *headings):
    kept = [body for heading, body in _sections(text) if heading not in headings]
    return "".join(kept)


def _clean(text):
    # Section dividers left dangling after removed sections.
    return re.sub(r"(?:\n---\n\s*)+(?=\n## |\Z)", "\n", text).strip() + "\n"


def on_files(files, config):
    root = os.path.dirname(os.path.abspath(config.config_file_path))
    with open(os.path.join(root, "README.md"), encoding="utf-8") as f:
        root_md = f.read()
    with open(os.path.join(config.docs_dir, "README.md"), encoding="utf-8") as f:
        current_md = f.read()

    contributing = "".join(b for h, b in _sections(root_md) if h == "## Contributing")
    root_md = _drop(root_md, "## Table of Contents", "## Contributing")
    root_md = root_md.replace(
        "See the [Table of Contents](#table-of-contents) below, or browse the "
        "[current version](current-version/README.md).",
        "Use the navigation menu to browse every topic.",
    )

    # Split root README: everything before "Previous versions" goes first, the rest last.
    head, tail = root_md, ""
    idx = root_md.find("## Previous versions")
    if idx != -1:
        head, tail = root_md[:idx], root_md[idx:]

    # current-version README without its Table of Contents, as a separate page.
    about = _drop(current_md, "## Table of Contents")
    about = re.sub(r"\A# .*\n", "# About the current version\n", about)

    contributing = re.sub(r"\A## Contributing\n", "# Contributing\n", contributing)
    contributing = re.sub(r"(?m)^### ", "## ", contributing)

    page = f"{head.rstrip()}\n\n{tail}"
    page = page.replace(
        "Use the navigation menu to browse every topic.",
        "Use the navigation menu to browse every topic, or read [about the current version](about.md) and [how to contribute](contribute.md).",
    )

    # Links that only make sense from the repository root.
    page = page.replace("](current-version/", "](")
    page = page.replace("](old-versions/)", f"]({REPO}/tree/master/old-versions)")
    page = page.replace("](LICENSE.md)", f"]({REPO}/blob/master/LICENSE.md)")
    page = page.replace("](doc-utilities/README.md)", f"]({REPO}/blob/master/doc-utilities/README.md)")
    contributing = contributing.replace(
        "](doc-utilities/README.md)", f"]({REPO}/blob/master/doc-utilities/README.md)"
    )

    # Images from the repository-level assets folder are copied into the site.
    for name in re.findall(r"\]\(/assets/images/([^)]+)\)", page):
        files.append(
            File(
                f"assets/images/{name}",
                root,
                config.site_dir,
                config.use_directory_urls,
            )
        )
    page = page.replace("](/assets/images/", "](assets/images/")

    # Replace the stock README-as-index with the combined page.
    for f in list(files):
        if f.src_uri == "README.md":
            files.remove(f)
    files.append(File.generated(config, "index.md", content=_clean(page)))
    files.append(File.generated(config, "contribute.md", content=_clean(contributing)))
    files.append(File.generated(config, "about.md", content=_clean(about)))
    return files
