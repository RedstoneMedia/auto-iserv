import pathlib
from setuptools import setup, find_packages


HERE = pathlib.Path(__file__).parent


README = (HERE / "README.md").read_text()


setup(
    name="auto-iserv",
    version="0.1.0",
    description="A Library that can be used to create tools to automate Iserv without an API key",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/RedstoneMedia/py_swagger_generator",
    author="RedstoneMedia",
    keywords="Iserv automation library auto",
    license="GNU General Public License v3.0",
    packages=["autoIserv", "autoIservCredGen"],
    include_package_data=True,
    install_requires=["PyYAML>=5.3.1", "selenium>=3.141.0", "requests>=2.23.0", "urllib3>=1.25.8", "pycryptodomex>=3.9.8"],
    entry_points={
        "console_scripts": [
            "gen-iserv-credential=autIservCredGen.__main__:main",
        ]
    },
)