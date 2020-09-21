from setuptools import setup, find_namespace_packages


setup(
    name="changelog-generator",
    version="0.1.0dev",
    packages=find_namespace_packages(include=["changelog_generator.*"]),
    maintainer="LumApps core team",
    maintainer_email="core@lumapps.com",
    url="https://github.com/lumapps/changelog-generator",
    python_requires="~=3.7",
    setup_requires=["wheel"],
    install_requires=["gitpython"],
    extras_require={},
    package_data={},
    test_suite="tests",
)
