from setuptools import setup

setup(
    name='ubuntudesign-asset-mapper',
    version='0.10',
    author='Robin',
    author_email='robin.winslow@canonical.com',
    url='https://github.com/ubuntudesign/asset-mapper',
    packages=[
        'ubuntudesign'
    ],
    description=(
        'A mapping class for using the Ubuntu asset server.'
    ),
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    install_requires=[
        "requests >= 2.0"
    ]
)
