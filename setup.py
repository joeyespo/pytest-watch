import io
import os
from setuptools import setup, find_packages


def read(filename):
    filepath = os.path.join(os.path.dirname(__file__), filename)
    with io.open(filepath, mode='r', encoding='utf-8') as f:
        return f.read()


setup(
    name='pytest-watch',
    version='4.2.0',
    description='Local continuous test runner with pytest and watchdog.',
    long_description=read('README.rst'),
    author='Joe Esposito',
    author_email='joe@joeyespo.com',
    url='http://github.com/joeyespo/pytest-watch',
    license='MIT',
    platforms='any',
    packages=find_packages(),
    install_requires=read('requirements.txt').splitlines(),
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Software Development :: Testing',
    ],
    entry_points={
        'console_scripts': [
            'pytest-watch = pytest_watch:main',
            'ptw = pytest_watch:main',
        ]
    },
)
