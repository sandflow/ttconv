"""A setuptools based setup module.
"""

import pathlib
from setuptools import setup, find_packages

here = pathlib.Path(__file__).parent.resolve()

long_description = (here / 'README.md').read_text(encoding='utf-8')

setup(
    name='ttconv', 
    version='1.0.5',
    description='Library for conversion of common timed text formats',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/sandflow/ttconv',
    author='Sandflow Consulting LLC',
    author_email='info@sandflow.com',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'Environment :: Console',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Multimedia'
    ],
    keywords='ttml, timed text, caption, subtitle, imsc, scc, srt, stl, smpte-tt, conversion, vtt, webvtt, 608',

    package_dir={'ttconv': 'src/main/python/ttconv'}, 

    packages=find_packages(where='src/main/python'),

    python_requires='>=3.7, <4',

    project_urls={
        'Bug Reports': 'https://github.com/sandflow/ttconv/issues',
        'Source': 'https://github.com/sandflow/ttconv',
    },

    entry_points={
        "console_scripts": [
            "tt = ttconv.tt:main"
        ]
    },
)
