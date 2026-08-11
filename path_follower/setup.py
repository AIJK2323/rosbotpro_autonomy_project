
from setuptools import find_packages, setup

package_name = "path_follower"

setup(
    name=package_name,
    version="0.0.1",

    packages=find_packages(exclude=["test"]),

    data_files=[
        (
            "share/ament_index/resource_index/packages",
            ["resource/" + package_name],
        ),
        (
            "share/" + package_name,
            ["package.xml"],
        ),
    ],

    install_requires=["setuptools"],

    zip_safe=True,

    maintainer="your_name",

    maintainer_email="your_email@example.com",

    description="Waypoint path follower",

    license="Apache-2.0",

    entry_points={
        "console_scripts": [

            "path_follower_node = path_follower.path_follower_node:main",

        ],
    },
)
