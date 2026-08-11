from setuptools import setup, find_packages
from glob import glob
import os

package_name = "d455_yolo_detector"

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

        (
            os.path.join(
                "share",
                package_name,
                "launch",
            ),
            glob("launch/*.py"),
        ),

    ],

    install_requires=[
        "setuptools",
    ],

    zip_safe=True,

    maintainer="radar",

    maintainer_email="radar@todo.todo",

    description="D455 YOLO perception pipeline",

    license="Apache-2.0",

    tests_require=[
        "pytest",
    ],

    entry_points={
        "console_scripts":[

            "yolo_detector_node=d455_yolo_detector.yolo_detector_node:main",

            "yolo_depth_3d_detector=d455_yolo_detector.yolo_depth_3d_detector:main",

            "object_tracker_node=d455_yolo_detector.object_tracker_node:main",

        ],
    },
)
