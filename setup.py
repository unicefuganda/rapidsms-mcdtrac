from setuptools import setup

setup(
    name='rapidsms-mcdtrac',
    version='0.1',
    license="BSD",

    install_requires = ["rapidsms", 'rapidsms-generic'],

    dependency_links = [
        "http://github.com/unicefuganda/rapidsms-generic/tarball/master#egg=rapidsms-generic"
    ],

    description='Quarterly Accelerated Approach Child Days Vaccination Tracking',
    long_description=open('README.rst').read(),
    author='Alfred Assey',
    author_email='asseym@gmail.com',

    url='http://github.com:/unicefuganda/rapidsms-mcdtrac',
    download_url='http://github.com:/unicefuganda/rapidsms-mcdtrac/downloads',

    include_package_data=True,

    packages=['mcdtrac'],
    package_data={'mcdtrac':['templates/*/*.html','templates/*/*/*.html','static/*/*']},
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ]
)
