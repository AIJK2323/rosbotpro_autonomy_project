from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():

    return LaunchDescription([
        Node(
            package="navigation_manager",
            executable="navigation_manager_node",
            output="screen",
        ),
    ])
