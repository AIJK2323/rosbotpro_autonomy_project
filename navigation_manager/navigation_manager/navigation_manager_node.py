#!/usr/bin/env python3

import rclpy

from rclpy.node import Node

from navigation_msgs.msg import NavigationCommand
from navigation_msgs.msg import ObstacleState


class NavigationManager(Node):

    def __init__(self):

        super().__init__("navigation_manager")

        ####################################################
        # Publisher
        ####################################################

        self.command_pub = self.create_publisher(
            NavigationCommand,
            "/navigation_command",
            10,
        )

        ####################################################
        # Subscribers
        ####################################################

        # Path follower
        self.create_subscription(
            NavigationCommand,
            "/path_command",
            self.path_callback,
            10,
        )

        # N10P obstacle state
        self.create_subscription(
            ObstacleState,
            "/obstacle_state",
            self.obstacle_callback,
            10,
        )

        # Human behavior
        self.create_subscription(
            NavigationCommand,
            "/human_command",
            self.human_callback,
            10,
        )

        ####################################################
        # Latest Commands
        ####################################################

        self.path_command = None
        self.human_command = None
        self.obstacle_state = None

        ####################################################
        # Last Receive Times
        ####################################################

        now = self.get_clock().now()

        self.path_time = now
        self.human_time = now
        self.obstacle_time = now

        ####################################################
        # Command Timeout
        ####################################################

        self.command_timeout = 0.5

        ####################################################
        # Control Loop
        ####################################################

        self.timer = self.create_timer(
            0.05,
            self.control_loop,
        )

        self.get_logger().info(
            "Navigation Manager Started"
        )

        self.get_logger().info(
            "Subscribed to /path_command"
        )

        self.get_logger().info(
            "Subscribed to /obstacle_state"
        )

        self.get_logger().info(
            "Subscribed to /human_command"
        )

    ####################################################
    # Callbacks
    ####################################################

    def path_callback(self, msg):

        self.path_command = msg
        self.path_time = self.get_clock().now()

    def obstacle_callback(self, msg):

        self.obstacle_state = msg
        self.obstacle_time = self.get_clock().now()

    def human_callback(self, msg):

        self.human_command = msg
        self.human_time = self.get_clock().now()

    ####################################################
    # Helper Functions
    ####################################################

    def command_is_valid(self, last_time):

        age = (
            self.get_clock().now() - last_time
        ).nanoseconds / 1e9

        return age < self.command_timeout

    ####################################################
    # Publish STOP
    ####################################################

    def publish_stop(self):

        msg = NavigationCommand()

        msg.linear_velocity = 0.0
        msg.angular_velocity = 0.0
        msg.state = "STOP"

        self.command_pub.publish(msg)

    ####################################################
    # Publish obstacle response
    ####################################################

    def process_obstacle(self):

        if self.obstacle_state is None:
            return False

        if not self.command_is_valid(
            self.obstacle_time
        ):
            return False

        state = self.obstacle_state.state

        ################################################
        # BLOCKED
        ################################################

        if state == "BLOCKED":

            self.publish_stop()

            self.get_logger().debug(
                "Obstacle BLOCKED - robot stopped"
            )

            return True

        ################################################
        # NO SCAN
        ################################################

        if state == "NO_SCAN":

            self.publish_stop()

            self.get_logger().warn(
                "No valid LiDAR scan - robot stopped"
            )

            return True

        ################################################
        # CAUTION
        ################################################

        if state == "CAUTION":

            # If we have a valid path command,
            # reduce forward velocity by 50%.
            #
            # We do NOT invent a steering direction
            # because the current ObstacleState message
            # contains only state + distance.

            if (
                self.path_command is not None
                and self.command_is_valid(
                    self.path_time
                )
            ):

                msg = NavigationCommand()

                msg.linear_velocity = (
                    self.path_command.linear_velocity * 0.5
                )

                msg.angular_velocity = (
                    self.path_command.angular_velocity
                )

                msg.state = "CAUTION"

                self.command_pub.publish(msg)

            else:

                self.publish_stop()

            self.get_logger().debug(
                "Obstacle CAUTION - reducing speed"
            )

            return True

        ################################################
        # CLEAR
        ################################################

        if state == "CLEAR":

            return False

        ################################################
        # Unknown state
        ################################################

        self.get_logger().warn(
            f"Unknown obstacle state: {state}"
        )

        self.publish_stop()

        return True

    ####################################################
    # Control Loop
    ####################################################

    def control_loop(self):

        ####################################################
        # Priority 1:
        # N10P Obstacle Safety
        ####################################################

        obstacle_handled = self.process_obstacle()

        if obstacle_handled:
            return

        ####################################################
        # Priority 2:
        # Human Behavior
        ####################################################

        if (
            self.human_command is not None
            and self.command_is_valid(
                self.human_time
            )
        ):

            self.command_pub.publish(
                self.human_command
            )

            self.get_logger().debug(
                "Using human command"
            )

            return

        ####################################################
        # Priority 3:
        # Path Follower
        ####################################################

        if (
            self.path_command is not None
            and self.command_is_valid(
                self.path_time
            )
        ):

            self.command_pub.publish(
                self.path_command
            )

            self.get_logger().debug(
                "Using path command"
            )

            return

        ####################################################
        # No Valid Commands
        ####################################################

        self.publish_stop()

        self.get_logger().warn(
            "No valid navigation command received. "
            "Robot stopped."
        )


def main(args=None):

    rclpy.init(args=args)

    node = NavigationManager()

    try:

        rclpy.spin(node)

    except KeyboardInterrupt:

        pass

    finally:

        node.destroy_node()

        rclpy.shutdown()


if __name__ == "__main__":

    main()
