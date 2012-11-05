from setuptools import setup, find_packages

setup(
    name='gitomatic',
    version='1.1.0',
    description='Git management tool',
    author='Jorge Eduardo Cardona',
    author_email='jorge.cardona@nuagehq.com',
    license="BSD",
    keywords="git",
    url="https://github.com/jorgeecardona/gitomatic",
    packages=['gitomatic'],
    test_suite='tests',
    entry_points={
        'console_scripts': [
            'gitomatic = gitomatic.main:main',
            'gitomatic-auth = gitomatic.auth:main',
            'gitomatic-configuration = gitomatic.configuration:main',
            ],
        },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: BSD License",
        ],
    install_requires=[
        'distribute',
        'argparse==1.2.1',
        'GitPython==0.3.2.RC1',
        ],
    setup_requires=[
        'mock==0.8.0'
        ]
    )
