# Always prefer setuptools over distutils
from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

# Get the long description from the README file
long_description = (here / 'README.md').read_text(encoding='utf-8')

setup(
    name='sevco-shell',
    version='0.0.1',
    description='Sevco Shell',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/sevincit/sevco-shell',
    author='Sevco',
    author_email='support@sevco.io',

    packages=find_packages(include=['sevco_shell', 'sevco_shell.*']),
    python_requires='>=3.7, <4',

    install_requires=[
        'requests>=2.24.0',
        'colorama>=0.4.3',
        'toml>=0.10.1',
        'dacite>=1.5.1',
        'python-dateutil>=2.8.1',
        'PyJWT>=1.7.1',
    ],

    entry_points={
        'console_scripts': [
            'svsh=sevco_shell.shell:main',
        ],
    },

    project_urls={  # Optional
        'Bug Reports': 'https://github.com/sevincit/sevco-shell/issues',
        'Source': 'https://github.com/sevincit/sevco-shell/',
    },
)
