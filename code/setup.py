import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

with open('LICENSE') as f:
    licensetext = f.read()

setuptools.setup(
    name="households", 
    version="0.1",
    author="Andrew Cabaniss",
    author_email="ahfc@umich.edu",
    description="Agent-based demographic model of individuals, households, and houses",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/acabaniss/house-inheritance",
    packages=setuptools.find_packages(),
    license=licensetext
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)