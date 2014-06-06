from setuptools import setup

setup(
    name='tt_twitter',
    description='TipTap client for Twitter API.',
    long_description=(
        '%s\n\n%s' % (
            open('README.md').read(),
            open('CHANGELOG.md').read()
        )
    ),
    version=open('VERSION').read().strip(),
    author='TipTap',
    install_requires=['twython'],
    package_dir={'tt_twitter': 'src'},
    packages=['tt_twitter']
)
