from setuptools import setup, find_packages

setup(
    name='waff',
    version='0.12',
    description='Waff is Waffle (a feature flipper for Django) without a database backend.',
    long_description=open('README.rst').read(),
    author='Waff Authors',
    author_email='DL-QuickOrderTeam@marks-and-spencer.com',
    license='BSD',
    packages=find_packages(exclude=['test_app', 'test_settings']),
    include_package_data=True,
    package_data={'': ['README.rst']},
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
