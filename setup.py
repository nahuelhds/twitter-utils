from setuptools import setup

setup(
    name='The Twitter Helper',
    version='0.1',
    py_modules=['twh'],
    install_requires=[
        'Click',
    ],
    entry_points='''
        [console_scripts]
        twh=twh:cli
    ''',
)