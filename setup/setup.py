from setuptools import find_packages, setup
setup(
    name='mdbaas',
    packages=find_packages(include=[
        'mdbaas',
        'mdbaas.errors',
        'mdbaas.opsmgrutil',
        'mdbaas.util',
    ], exclude=[
    ]),
    version='0.1.1',
    description='MDBaaS Library (BNY)',
    author='Errol Kutan',
    license='No license',
    install_requires=[
        'certifi',
        'charset-normalizer',
        'idna',
        'pymongo',
        'PyYAML',
        'requests',
        'urllib3'
    ],
)
