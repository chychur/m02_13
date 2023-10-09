import sys
import os
#sys.path.append(os.path.abspath('..'))
#sys.path.insert(0, os.path.abspath(os.path.join('..', '..', '..', 'src')))

basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, basedir)

project = 'AddressBook'
copyright = '2023, Andrii Chychur'
author = 'Andrii Chychur'
release = '1.0'


extensions = ['sphinx.ext.autodoc', 'sphinx.ext.napoleon']

napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = False
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_preprocess_types = False
napoleon_type_aliases = None
napoleon_attr_annotations = True


templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

html_theme = 'nature'
html_static_path = ['_static']
