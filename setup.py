from setuptools import setup

setup(
    name='interceptor',
    version='1.0a1',
    author='Piotr Maślanka',
    install_requires=['satella'],
    package_data={'interceptor': ['templates/cmdline.py']},
    packages=[
        'interceptor',
    ],
    entry_points={
        'console_scripts': [
            'intercept = interceptor.intercept:run'
        ]
    },
)
