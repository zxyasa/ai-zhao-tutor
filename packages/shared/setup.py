from setuptools import setup, find_packages

setup(
    name="mathcoach-shared",
    version="0.1.0",
    description="Shared Pydantic schemas for MathCoach platform",
    packages=find_packages(),
    install_requires=[
        "pydantic>=2.0.0",
    ],
    python_requires=">=3.11",
)
