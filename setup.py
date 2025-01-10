#  Created by Martin Strohalm, Thermo Fisher Scientific

from setuptools import setup, find_packages

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
    version = '5.3.0',
    description = 'Provides easy access to Thermo Discoverer platform results.',
    url = 'https://github.com/thermofisherlsms/pyeds',
    author = 'Martin Strohalm, Thermo Fisher Scientific',
    author_email = '',
    license = 'MIT',
    packages = find_packages(),
    package_data = package_data,
    classifiers = classifiers,
    install_requires = ['numpy'],
    zip_safe = False)
