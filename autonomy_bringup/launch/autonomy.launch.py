from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():

    return LaunchDescription([

        #
        # Path Follower
        #
        Node(
            package="path_follower",
            executable="path_follower_node",
            name="path_follower",
            output="screen",
        ),

        #
        # Obstacle Avoidance
        #
        Node(
            package="obstacle_avoidance",
            executable="obstacle_avoidance_node",
            name="obstacle_avoidance",
            output="screen",
        ),

        #
        # Human Behavior
        #
        Node(
            package="human_behavior",
            executable="human_behavior_node",
            name="human_behavior",
            output="screen",
        ),

        #
        # Navigation Manager
        #
        Node(
            package="navigation_manager",
            executable="navigation_manager_node",
            name="navigation_manager",
            output="screen",
        ),

        #
        # Navigation to Rosbot
        #
        Node(
            package="navigation_to_rosbot",
            executable="navigation_to_rosbot_node",
            name="navigation_to_rosbot",
            output="screen",
        ),
    ])
