#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = ['Click>=7.0', 'click_log>=0.3.2', 'pandas>=1.0.0', 'xlrd>=1.2.0']

setup_requirements = [ ]

test_requirements = [ ]

setup(
    author="Ronak Shah",
    author_email='rons.shah@gmail.com',
    python_requires='>=3.5',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="Project to genotype SNV, INDEL and SV.",
    entry_points={
        'console_scripts': [
            'genotype_variants=genotype_variants.cli:main',
        ],
    },
    install_requires=requirements,
    license="Apache Software License 2.0",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='genotype_variants',
    name='genotype_variants',
    packages=find_packages(include=['genotype_variants', 'genotype_variants.*']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/msk-access/genotype_variants',
    version='0.3.0',
    zip_safe=False,
)
