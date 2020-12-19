import setuptools



with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="eric_bot", # Replace with your own username
    version="0.0.1",
    author="320834",
    author_email="justinchen1000@gmail.com",
    description="A discord bot for emulating our friend eric",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/320834/Eric-Bot",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)