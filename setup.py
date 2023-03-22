#  Created by Martin Strohalm, Thermo Fisher Scientific

import os.path

from setuptools import setup, find_packages

def get_version(rel_path):
    here = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(here, rel_path)) as fp:
      for line in fp.read().splitlines():
          if line.startswith('version'):
              return '.'.join(map(str, eval(line.split('=')[1])))
      else:
          raise RuntimeError("Unable to find version string.")
        
# include additional files
package_data = {
    '': ['*.css', '*.js']}

# set classifiers
classifiers = [
    'Development Status :: 4 - Beta',
    'Programming Language :: Python :: 3 :: Only',
    'Operating System :: OS Independent',
    'Topic :: Scientific/Engineering',
    'Intended Audience :: Science/Research']

# main setup
setup(
    name = 'pyeds',
    version = get_version('pyeds/__init__.py'),
    description = 'Provides easy access to Thermo Discoverer platform results.',
    url = 'https://github.com/thermofisherlsms/pyeds',
    author = 'Martin Strohalm, Thermo Fisher Scientific',
    author_email = '',
    license = 'MIT',
    packages = find_packages(),
    package_data = package_data,
    classifiers = classifiers,
    install_requires = ['numpy'],
    extras_require = {'display': ['rdkit-pypi', 'matplolib']},
    zip_safe = False)
