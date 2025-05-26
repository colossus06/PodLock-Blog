# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information


# def setup(app):
#     # (create a setup() function if you don't already have one;
#     # or add to the existing setup() ...)

html_title = ' '

project = 'PodLock'
# release = '2024'

html_show_copyright=True
html_show_sourcelink = False

html_show_sphinx = False

extensions = [ 
    "myst_parser",
    # "sphinx-social-previews",
    "sphinxext.opengraph",
    "sphinx_design",
    "sphinx_comments"
]

comments_config = {
   "utterances": {
      "repo": "colossus06/PodLock-Blog",
      "optional": "config",
   }
}
# -- Project information
# copyright = "2025, PodLock"
author = "Gulcan Topcu"
# ogp_site_url = "https://PodLock.devtechops.dev/"
ogp_type = "article"
ogp_image = "https://raw.githubusercontent.com/colossus06/PodLock-Blog/main/images/mylogo.png"
ogp_use_first_image= True
ogp_enable_meta_description=True
ogp_social_cards = {
    "enable": True,
    "font": "Noto Sans CJK JP"
}

templates_path = ['_templates']

exclude_patterns = [
    "tracking/**",
    "venv",
    "_build",
    "Thumbs.db",
    ".DS_Store",
    "*import_posts*",
    "**/pandoc_ipynb/inputs/*",
    "README.md",
    "**/.ipynb_checkpoints/*",
    "docs",
]

source_suffix = ['.rst', '.md']

html_favicon = 'images/favicon.png'

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

copyright = "2025, PodLock. All rights reserved"

html_logo= "images/mylogo.png"

html_theme = 'furo'
html_static_path = ['_static']

html_css_files = ["css/custom.css"]


html_theme_options = {
    'navigation_with_keys': True,
    # "announcement": "PodLock 💛 Hands-on Only 🏭",
    "light_css_variables": {
        # "font-stack": "Ubuntu, sans-serif",
        # "font-stack--monospace": "Oswald, monospace",
        "color-brand-primary": "#13306D",
        "color-brand-content": "#b86767"
    },
    "dark_css_variables": {
        # "font-stack": "Ubuntu, sans-serif",
        # "font-stack--monospace": "Oswald, monospace",
        "color-brand-primary": "#AC6BF6",
        "color-brand-content": "#FFEBD8"
        # #10CD23
    },

}

# html_js_files = [
#     'js/random_blue.js'
# ]

# These are options specifically for the Wagtail Theme.
myst_enable_extensions = [
    "amsmath",
    "attrs_inline",
    "colon_fence",
    "dollarmath",
    "fieldlist",
    "html_admonition",
    "html_image",
    "replacements",
    "smartquotes",
    "strikethrough",
    "substitution",
    "tasklist",
]

html_context = {
    "display_github": False, # Add 'Edit on Github' link instead of 'View page source'
    "last_updated": False,
    "commit": False,
    "default_mode": "light"
}


master_doc = 'index'