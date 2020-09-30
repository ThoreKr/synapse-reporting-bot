import setuptools

setuptools.setup(
    name="reporting-bot",
    version="0.0.1",
    author="ThoreKr",
    author_email="thore@scimeda.de",
    description="Reporting Bot for synapse event_reports table",
    long_description="",
    long_description_content_type="text/markdown",
    url="https://github.com/ThoreKr/synapse-reporting-bot",
    packages=setuptools.find_packages(),
    install_requires=[
        "matrix-nio[e2e]>=0.10.0",
        "environ-config==20.1.0",
        "psycopg2>=2.8.5",
    ],
    classifiers=[
        "Programming Language :: Python :: 3"
    ],
    python_requires='>=3.7',
    scripts=["reporting-bot"]
)
