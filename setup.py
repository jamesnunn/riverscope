from pip.req import parse_requirements
from setuptools import setup

from riverscope._version import __app_name__, __version__

requirements = parse_requirements('./requirements.txt', session=False)

dev_requirements = parse_requirements('./requirements_dev.txt', session=False)


setup(
    name=__app_name__,
    version=__version__,
    packages=['riverscope'],
    install_requires=[str(requirement.req) for requirement in requirements],
    extras_require={
        'dev': [str(requirement.req) for requirement in dev_requirements]
    },
    dependency_links=['http://github.com/jamesnunn/logger/tarball/master#egg=logger'],
    entry_points={
      'console_scripts': [
          'cache_stations = riverscope.utils.cli:cache_stations',
        ]
    },

  )

