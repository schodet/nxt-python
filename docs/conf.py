# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys

sys.path.insert(0, os.path.abspath(".."))


# -- Project information -----------------------------------------------------

project = "NXT-Python"
copyright = "2021-2025, Nicolas Schodet"
author = "Nicolas Schodet"

# The full version, including alpha/beta/rc tags
release = "3.5.1"
version = release


# -- General configuration ---------------------------------------------------

# If your documentation needs a minimal Sphinx version, state it here.
#
needs_sphinx = "3.4"

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
]

intersphinx_mapping = {"python": ("https://docs.python.org/3", None)}

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build"]

nitpicky = True

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "sphinx_rtd_theme"

html_logo = "../logo.svg"
html_favicon = "favicon.ico"
html_copy_source = False

# -- Options for Man pages output --------------------------------------------

man_pages_authors = [
    "This program is part of NXT-Python which is currently maintained by"
    " Nicolas Schodet.",
]

man_pages = [
    (
        "config",
        "nxt-python.conf",
        "NXT-Python configuration file",
        man_pages_authors,
        5,
    ),
    (
        "commands/nxt-push",
        "nxt-push",
        "Push files to a NXT brick",
        man_pages_authors,
        1,
    ),
    (
        "commands/nxt-screenshot",
        "nxt-screenshot",
        "Capture screen utility for the NXT brick",
        man_pages_authors,
        1,
    ),
    (
        "commands/nxt-server",
        "nxt-server",
        "Network server for the NXT brick",
        man_pages_authors,
        1,
    ),
    (
        "commands/nxt-test",
        "nxt-test",
        "Test the NXT-Python setup",
        man_pages_authors,
        1,
    ),
]

# -- Options for autodoc -----------------------------------------------------

autodoc_member_order = "bysource"
autodoc_typehints = "description"
