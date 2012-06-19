from setuptools import setup, find_packages

setup(
    name='gitomatic',
    version='1.0a3',
    description='Git management tool',
    author='Jorge Eduardo Cardona',
    author_email='jorge.cardona@nuagehq.com',
    license="BSD",
    keywords="git",
    url="https://github.com/jorgeecardona/gitomatic",
    packages=find_packages(),
    test_suite='test',
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
        'configobj==4.7.2',
        'argparse==1.2.1',
        'GitPython==0.3.2.RC1',
        ],
    setup_requires=[
        'mock==0.8.0'
        ]
    )
