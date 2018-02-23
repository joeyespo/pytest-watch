import os
import sys
from setuptools import setup, find_packages


def read(filename):
    with open(os.path.join(os.path.dirname(__file__), filename)) as f:
        return f.read()


DEPS_MAIN = ["colorama>=0.3.3", "docopt>=0.6.2", "pytest>=2.6.4",
             "watchdog>=0.6.0"]
DEPS_TESTING = ["pytest-mock>=1.7.0"]
DEPS_QA = DEPS_TESTING + ["pytest-cov>=2.5.1"]


setup(
    name='pytest-watch',
    version='4.1.0',
    description='Local continuous test runner with pytest and watchdog.',
    long_description=read('README.md'),
    author='Joe Esposito',
    author_email='joe@joeyespo.com',
    url='http://github.com/joeyespo/pytest-watch',
    license='MIT',
    platforms='any',
    packages=find_packages(),
    install_requires=DEPS_MAIN,
    tests_require=DEPS_TESTING,
    entry_points={
        'console_scripts': [
            'pytest-watch = pytest_watch:main',
            'ptw = pytest_watch:main',
        ]
    },
    extras_require={
        'testing': DEPS_TESTING,
        'dev': DEPS_TESTING + DEPS_QA + ['pdbpp', 'pytest-pdb'],
        'qa': DEPS_QA,
        'testing:python_version in "2.6, 2.7, 3.2"': ['mock'],
        'dev:python_version in "2.6, 2.7, 3.2"': ['mock'],
        'qa:python_version in "2.6, 2.7, 3.2"': ['mock'],
    },
)
