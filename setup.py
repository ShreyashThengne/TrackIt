from setuptools import setup

setup(
    name = 'trackit',
    version = '1.0',
    packages = ['trackit'],
    entry_points = {
        'console_scripts' : [
            'trackit = trackit.cli:main',
            ]
    }
)
