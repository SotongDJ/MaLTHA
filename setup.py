import setuptools

setuptools.setup(
    name = "MaLTHA",
    version = "0.3.2",
    author = "David Soh",
    author_email = "ln@trth.nl",
    description = "MaLTHA works as a static site generator that use Markdown format with TOML/HTML hybrid annotation.",
    long_description = open('README.md').read(),
    long_description_content_type = 'text/markdown',
    url = "https://github.com/SotongDJ/MaLTHA",
    packages = ["MaLTHA"],
    keywords = [],
    classifiers = [
        "Development Status :: 4 - Beta",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "rtoml",
        "markdown2",
        "Pygments",
    ],
)
