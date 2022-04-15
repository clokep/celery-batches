import os
import sys
from importlib import metadata

sys.path.insert(0, os.path.abspath(".."))
sys.path.insert(0, os.path.abspath("./_ext"))

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx_celery.setting_crossref",
    "celerydocs",
]

templates_path = ["_templates"]

source_suffix = ".rst"

master_doc = "index"

project = "Celery Batches"
copyright = "2017, Percipient Networks; 2020-, Patrick Cloke"
author = "Patrick Cloke"

release = metadata.version("celery-batches")
version = ".".join(release.split(".")[0:2])

language = None

exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

pygments_style = "sphinx"

html_theme = "furo"

html_sidebars = {
    "**": [
        "sidebar/scroll-start.html",
        "sidebar/brand.html",
        "sidebar/search.html",
        "sidebar/navigation.html",
        "sidebar/ethical-ads.html",
        "sidebar/scroll-end.html",
    ]
}

htmlhelp_basename = "CeleryBatchesdoc"

latex_documents = [
    (
        master_doc,
        "CeleryBatches.tex",
        "Celery Batches Documentation",
        "Percipient Networks",
        "manual",
    ),
]

man_pages = [(master_doc, "celerybatches", "Celery Batches Documentation", [author], 1)]

texinfo_documents = [
    (
        master_doc,
        "CeleryBatches",
        "Celery Batches Documentation",
        author,
        "CeleryBatches",
        "One line description of project.",
        "Miscellaneous",
    ),
]

INTERSPHINX_MAPPING = {
    "python": ("http://docs.python.org/dev/", None),
    "kombu": ("http://kombu.readthedocs.io/en/master/", None),
    "celery": ("http://docs.celeryproject.org/en/master", None),
}
