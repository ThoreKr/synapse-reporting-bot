import setuptools

setuptools.setup(
    name="reporting-bot",
    version="0.1.0",
    author="ThoreKr",
    author_email="thore@scimeda.de",
    description="Reporting Bot for synapse event_reports table",
    long_description="",
    long_description_content_type="text/markdown",
    url="https://github.com/ThoreKr/synapse-reporting-bot",
    packages=setuptools.find_packages(),
    install_requires=[
        "matrix-nio>=0.24.0",
        "environ-config==23.2.0",
        "psycopg2>=2.9.9",
    ],
    classifiers=[
        "Programming Language :: Python :: 3"
    ],
    python_requires='>=3.9',
    scripts=["reporting-bot"]
)
