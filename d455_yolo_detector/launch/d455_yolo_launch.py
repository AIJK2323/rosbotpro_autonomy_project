from launch import LaunchDescription

from launch.actions import IncludeLaunchDescription
from launch.actions import TimerAction

from launch.launch_description_sources import PythonLaunchDescriptionSource

from launch_ros.actions import Node

from ament_index_python.packages import get_package_share_directory

import os



def generate_launch_description():



    # =====================================
    # RealSense D455
    # =====================================

    camera = IncludeLaunchDescription(

        PythonLaunchDescriptionSource(

            os.path.join(

                get_package_share_directory(
                    "realsense2_camera"
                ),

                "launch",

                "rs_launch.py"

            )

        ),

        launch_arguments={

            "enable_color":"true",

            "enable_depth":"true",

            "align_depth.enable":"true",


            "rgb_camera.color_profile":
                "1280x720x15",


            "depth_module.depth_profile":
                "640x480x15",


            "enable_gyro":"false",

            "enable_accel":"false"

        }.items()

    )



    # =====================================
    # YOLO 2D Detector
    # =====================================

    yolo = Node(

        package="d455_yolo_detector",

        executable="yolo_detector_node",

        name="yolo_detector",

        output="screen"

    )



    # =====================================
    # Depth Projection
    # =====================================

    yolo_3d = Node(

        package="d455_yolo_detector",

        executable="yolo_depth_3d_detector",

        name="yolo_depth_3d_detector",

        output="screen"

    )



    # =====================================
    # Tracker
    # =====================================

    tracker = Node(

        package="d455_yolo_detector",

        executable="object_tracker_node",

        name="object_tracker",

        output="screen"

    )



    delayed_start = TimerAction(

        period=8.0,

        actions=[

            yolo,

            yolo_3d,

            tracker

        ]

    )



    return LaunchDescription([

        camera,

        delayed_start

    ])
