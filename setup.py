
from setuptools import setup, find_packages

from payeer import __version__


with open('requirements.txt') as f:
    requires = f.read().splitlines()


url = 'https://github.com/pmaigutyak/mp-payeer'


setup(
    name='django-payeer',
    version=__version__,
    description='Django payeer app',
    long_description=open('README.md').read(),
    author='Paul Maigutyak',
    author_email='pmaigutyak@gmail.com',
    url=url,
    download_url='%s/archive/%s.tar.gz' % (url, __version__),
    packages=find_packages(),
    include_package_data=True,
    license='MIT',
    install_requires=requires
)
