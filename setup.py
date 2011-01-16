from setuptools import setup, find_packages

setup(
    name='gitomatic',
    version='0.5.14',
    description='Git management tool',
    author='Jorge Eduardo Cardona',
    author_email='jorge.cardona@nuagehq.com',
    license="BSD",
    keywords="git",
    url="http://pypi.python.org/pypi/gitomatic/",
    packages=find_packages(),
    test_suite='gitomatic.test',
    entry_points={
        'console_scripts': [
            'gitomatic = gitomatic.main:main',
            'gitomatic-auth = gitomatic.auth:main',
            ],
        },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: BSD License",
        ],
    install_requires=[
        'configobj',
        'argparse',
        'GitPython',
        'simplejson',
        ],
    )
