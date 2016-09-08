import setuptools

setuptools.setup(
    name='txprop21',
    version='0.0.1',
    packages=setuptools.find_packages(),
    install_requires=[
        'Flask',
        'python-memcached',
        'PyYAML',
        'requests',
        'two1',
    ],
)
