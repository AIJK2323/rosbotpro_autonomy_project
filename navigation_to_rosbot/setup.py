from setuptools import find_packages, setup

package_name = "navigation_to_rosbot"

setup(
    name=package_name,
    version="0.0.0",
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
        (
            "share/" + package_name + "/launch",
            ["launch/navigation_to_rosbot.launch.py"],
        ),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="radar",
    maintainer_email="radar@todo.todo",
    description="Converts NavigationCommand messages into Twist commands for the Wheeltec robot.",
    license="Apache-2.0",
    extras_require={
        "test": [
            "pytest",
        ],
    },
    entry_points={
        "console_scripts": [
            "navigation_to_rosbot_node = navigation_to_rosbot.navigation_to_rosbot_node:main",
        ],
    },
)
