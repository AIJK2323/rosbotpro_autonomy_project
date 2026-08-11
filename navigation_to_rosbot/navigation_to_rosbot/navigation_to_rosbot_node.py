#!/usr/bin/env python3

import rclpy

from rclpy.node import Node

from geometry_msgs.msg import Twist
from navigation_msgs.msg import NavigationCommand


class NavigationToRosbot(Node):

    def __init__(self):

        super().__init__("navigation_to_rosbot")

        ####################################################
        # Publisher
        ####################################################

        self.cmd_vel_pub = self.create_publisher(
            Twist,
            "/cmd_vel",
            10,
        )

        ####################################################
        # Subscriber
        ####################################################

        self.create_subscription(
            NavigationCommand,
            "/navigation_command",
            self.navigation_callback,
            10,
        )

        ####################################################
        # Command timeout
        ####################################################

        self.command_timeout = 0.5

        self.last_command_time = None

        ####################################################
        # Safety timer
        ####################################################

        self.timer = self.create_timer(
            0.1,
            self.safety_check,
        )

        self.get_logger().info(
            "Navigation To Rosbot Started"
        )

        self.get_logger().info(
            "Command timeout: 0.50 seconds"
        )

    ####################################################
    # Navigation Callback
    ####################################################

    def navigation_callback(self, msg):

        self.last_command_time = self.get_clock().now()

        twist = Twist()

        ####################################################
        # Convert NavigationCommand -> Twist
        ####################################################

        twist.linear.x = msg.linear_velocity
        twist.linear.y = 0.0
        twist.linear.z = 0.0

        twist.angular.x = 0.0
        twist.angular.y = 0.0
        twist.angular.z = msg.angular_velocity

        ####################################################
        # Publish
        ####################################################

        self.cmd_vel_pub.publish(twist)

        self.get_logger().debug(
            f"Published cmd_vel: "
            f"linear={twist.linear.x:.2f}, "
            f"angular={twist.angular.z:.2f}, "
            f"state={msg.state}"
        )

    ####################################################
    # Safety Check
    ####################################################

    def safety_check(self):

        ####################################################
        # No command has ever been received
        ####################################################

        if self.last_command_time is None:

            self.publish_stop()

            return

        ####################################################
        # Calculate command age
        ####################################################

        age = (
            self.get_clock().now()
            - self.last_command_time
        ).nanoseconds / 1e9

        ####################################################
        # Stop if command is stale
        ####################################################

        if age > self.command_timeout:

            self.publish_stop()

            self.get_logger().warn(
                "Navigation command timeout - robot stopped"
            )

    ####################################################
    # Stop robot
    ####################################################

    def publish_stop(self):

        twist = Twist()

        twist.linear.x = 0.0
        twist.linear.y = 0.0
        twist.linear.z = 0.0

        twist.angular.x = 0.0
        twist.angular.y = 0.0
        twist.angular.z = 0.0

        self.cmd_vel_pub.publish(twist)


def main(args=None):

    rclpy.init(args=args)

    node = NavigationToRosbot()

    try:

        rclpy.spin(node)

    except KeyboardInterrupt:

        pass

    finally:

        node.publish_stop()

        node.destroy_node()

        rclpy.shutdown()


if __name__ == "__main__":

    main()
