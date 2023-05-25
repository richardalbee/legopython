#Package the pip according to Python documentation https://packaging.python.org/en/latest/specifications/
#Choosing a license https://gist.github.com/nicolasdao/a7adda51f2f185e8d2700e1573d8a633
'''Setup file for building a pip for a module.

INSTRUCTIONS FOR BUILDING A PIP https://pip.pypa.io/en/stable/cli/pip_wheel/

Install Prequisites: py -m pip install --upgrade pip setuptools wheel twine build
Build Pip Distributable: py -m build --wheel from the /PythonTools/ directory with this setup.py in it. #TODO: This only installs the dev version, figure out versioning.

#Developer Install: "py -m pip install -e ." from this folder.
#User Install: 

To build the pip module, increment the version number in the setup.py file and run the following command, uploading the generated package in dist/ for others to install and use.
'''
import os
from pathlib import Path
import setuptools

requires = [
    'boto3',
    'credstash',
    'psycopg2-binary',
    'requests',
    'pandas',
    'numpy',
    'configparser'
]

#Specify which scripts should be command line callable.
scripts = []
import_folders = ['legopython','scripts','external']
for folder in import_folders:
    for python_module in Path(folder).iterdir():
        if python_module.suffix == ".py":
            scripts.append(str(python_module))

setuptools.setup(
    name = 'legopython',
    version = os.getenv('PACKAGE_VERSION', '0.0.dev0'),
    description = 'Python library designed to make scripting easier with component-based development.',
    author = 'Richard Albee',
    author_email='ralbee1@iwu.edu',
    packages = setuptools.find_packages(),
    install_requires = requires,
    #entry_points = entry_points, #https://packaging.python.org/en/latest/specifications/entry-points/
    scripts = scripts,
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10'
    ],
    python_requires = '>=3.8',
    url = "https://github.com/ralbee1/legopython"
)
