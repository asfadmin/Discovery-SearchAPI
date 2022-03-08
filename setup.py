import setuptools

with open("README.md", "r", encoding="utf-8") as readme_file:
    readme = readme_file.read()

setuptools.setup(
    name="SearchAPI",
    author="Alaska Satellite Facility Discovery Team",
    author_email="uaf-asf-discovery@alaska.edu",
    description="Helper package to run the API.",
    long_description=readme,
    url="https://github.com/asfadmin/Discovery-SearchAPI.git",
    packages=setuptools.find_packages(),
    package_dir={"SearchAPI": "SearchAPI"},
    package_data={"SearchAPI": ["*.yml", "*.yaml"]},
)
