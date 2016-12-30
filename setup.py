import setuptools

setuptools.setup(
    name='txprop21',
    version='0.0.1',
    packages=setuptools.find_packages(),
    install_requires=[
        'Django==1.8.3',
        'djangorestframework==3.2.3',
        'Flask',
        'python-memcached',
        'PyYAML',
        'two1',
    ],
)
