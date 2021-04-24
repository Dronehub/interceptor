from setuptools import setup

setup(
    name='interceptor',
    version='2.0rc17',
    author='Piotr Maślanka',
    install_requires=['satella'],
    package_data={'interceptor': ['templates/cmdline.py',
                                  'templates/config']},
    packages=[
        'interceptor',
    ],
    entry_points={
        'console_scripts': [
            'intercept = interceptor.run:run'
        ]
    },
)
