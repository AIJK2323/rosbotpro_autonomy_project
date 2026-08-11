from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():

    return LaunchDescription([

        Node(
            package="path_follower",
            executable="path_follower_node",
            output="screen"
        )

    ])
