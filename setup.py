"""
This module is necessary to distribute and install the written module via pip
"""
from setuptools import setup

with open('README.md', 'r', encoding='utf8') as readme:
    readme_content = readme.read()
with open('CHANGELOG.md', 'r', encoding='utf8') as changelog:
    changelog_content = changelog.read()

setup(
    name='users',
    version='1.0.3',
    license='MIT',
    description=(
        "This module contains classes and functions for implementing"
        "the simplest authorization for telegram bots"
    ),
    py_modules=["users"],
    package_dir={'': 'users'},
    author='Oleg Bervinov',
    author_email='obervinov@pm.me',
    long_description=(f"{readme_content}""\n\n"f"{changelog_content}"),
    long_description_content_type="text/markdown",
    url='https://github.com/obervinov/users-package',
    include_package_data=True,
    classifiers=[
        "License :: OSI Approved :: MIT License",
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Operating System :: OS Independent'
    ],
    keywords=['users', 'authentication'],
    install_requires=[
        'logger @ git+https://github.com/obervinov/logger-package.git@v1.0.1#egg=logger-1.0.1',
        'vault @ git+https://github.com/obervinov/vault-package.git@v2.0.0#egg=vault-2.0.0',
    ]
)
