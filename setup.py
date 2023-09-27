from setuptools import setup
from src.act_as_api import __version__


def requirements_txt():
    return open('requirements.txt').read().split("\n")

setup(
    name='act-as-api',
    version=__version__,
    description='API for GPT personal management.',
    url='https://github.com/ddrscott/act-as-api',
    author='Scott Pierce',
    author_email='spierce@spins.com',
    package_dir={'':'src'},
    packages=['act_as_api'],
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    python_requires='>=3.11, < 3.12',
    install_requires=requirements_txt(),
    entry_points={
        'console_scripts':[
            "aaa = act_as_api.cli:cli"
        ],
    }
)
