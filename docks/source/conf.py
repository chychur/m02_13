import sys
import os
sys.path.append(os.path.abspath('..'))

project = 'AddressBook'
copyright = '2023, Andrii Chychur'
author = 'Andrii Chychur'
release = '1.0'

extensions = []

templates_path = ['_templates']
exclude_patterns = ['sphinx.ext.autodoc']

html_theme = 'nature'
html_static_path = ['_static']
