from setuptools import setup, find_packages
from os.path import join, dirname
import gzfuse

setup(
    name='gzfuse',
    author='Gautier Portet',
    author_email='gautier@soundconverter.org',
    url='http://kassoulet.free.fr',
    version=gzfuse.__version__,
    packages=find_packages(),
    long_description=open(join(dirname(__file__), 'README.markdown')).read(),
    entry_points={
        'console_scripts': [
            'gzfuse = gzfuse.gzfuse:main',
            ]
        },
    install_requires=[
        'fusepy'
    ]
    )
