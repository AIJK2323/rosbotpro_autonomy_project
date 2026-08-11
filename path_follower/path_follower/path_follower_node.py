#!/usr/bin/env python3

import math

import rclpy
from rclpy.node import Node

from nav_msgs.msg import Odometry
from navigation_msgs.msg import NavigationCommand


class PathFollower(Node):

    def __init__(self):

        super().__init__("path_follower")

        ####################################################
        # Robot Pose
        ####################################################

        self.x = 0.0
        self.y = 0.0
        self.yaw = 0.0
        self.pose_received = False

        ####################################################
        # Waypoints
        ####################################################

        self.waypoints = [
            (0.0, 0.0),
            (2.0, 0.0),
            (2.0, 2.0),
            (0.0, 2.0),
            (0.0, 0.0),
        ]

        self.current_waypoint = 0

        ####################################################
        # Controller Parameters
        ####################################################

        self.k_linear = 0.8
        self.k_angular = 2.0

        self.max_linear = 0.6
        self.max_angular = 1.2

        self.goal_tolerance = 0.25

        ####################################################
        # Subscribers
        ####################################################

        self.create_subscription(
            Odometry,
            "/odom_combined",
            self.odom_callback,
            10,
        )

        ####################################################
        # Publishers
        ####################################################

        self.publisher = self.create_publisher(
            NavigationCommand,
            "/path_command",
            10,
        )

        ####################################################
        # Control Loop
        ####################################################

        self.timer = self.create_timer(
            0.1,
            self.timer_callback,
        )

        self.get_logger().info("Path Follower Started")

    ########################################################

    def odom_callback(self, msg):

        self.pose_received = True

        self.x = msg.pose.pose.position.x
        self.y = msg.pose.pose.position.y

        q = msg.pose.pose.orientation

        siny = 2.0 * (
            q.w * q.z +
            q.x * q.y
        )

        cosy = 1.0 - 2.0 * (
            q.y * q.y +
            q.z * q.z
        )

        self.yaw = math.atan2(
            siny,
            cosy,
        )

    ########################################################

    def normalize_angle(self, angle):

        while angle > math.pi:
            angle -= 2.0 * math.pi

        while angle < -math.pi:
            angle += 2.0 * math.pi

        return angle

    ########################################################

    def clamp(self, value, minimum, maximum):

        return max(min(value, maximum), minimum)

    ########################################################

    def timer_callback(self):

        if not self.pose_received:
            return

        ####################################################
        # Mission Complete
        ####################################################

        if self.current_waypoint >= len(self.waypoints):

            cmd = NavigationCommand()

            cmd.linear_velocity = 0.0
            cmd.angular_velocity = 0.0
            cmd.state = "MISSION_COMPLETE"

            self.publisher.publish(cmd)

            return

        ####################################################
        # Current Goal
        ####################################################

        goal_x, goal_y = self.waypoints[self.current_waypoint]

        dx = goal_x - self.x
        dy = goal_y - self.y

        distance = math.sqrt(
            dx * dx +
            dy * dy
        )

        ####################################################
        # Waypoint Reached
        ####################################################

        if distance < self.goal_tolerance:

            self.get_logger().info(
                f"Reached waypoint {self.current_waypoint}"
            )

            self.current_waypoint += 1

            return

        ####################################################
        # Heading Error
        ####################################################

        desired_heading = math.atan2(
            dy,
            dx,
        )

        heading_error = self.normalize_angle(
            desired_heading - self.yaw
        )

        ####################################################
        # Proportional Controller
        ####################################################

        linear = self.k_linear * distance
        angular = self.k_angular * heading_error

        ####################################################
        # Reduce Speed During Sharp Turns
        ####################################################

        if abs(heading_error) > math.radians(45):
            linear *= 0.3

        ####################################################
        # Clamp Commands
        ####################################################

        linear = self.clamp(
            linear,
            0.0,
            self.max_linear,
        )

        angular = self.clamp(
            angular,
            -self.max_angular,
            self.max_angular,
        )

        ####################################################
        # Publish Command
        ####################################################

        cmd = NavigationCommand()

        cmd.linear_velocity = float(linear)
        cmd.angular_velocity = float(angular)
        cmd.state = "FOLLOW_PATH"

        self.publisher.publish(cmd)

        ####################################################
        # Debug Output
        ####################################################

        self.get_logger().info(

            f"Waypoint {self.current_waypoint} | "

            f"Position=({self.x:.2f}, {self.y:.2f}) | "

            f"Distance={distance:.2f} | "

            f"Heading Error={math.degrees(heading_error):.1f} deg | "

            f"Linear={linear:.2f} | "

            f"Angular={angular:.2f}"

        )


def main(args=None):

    rclpy.init(args=args)

    node = PathFollower()

    rclpy.spin(node)

    node.destroy_node()

    rclpy.shutdown()


if __name__ == "__main__":

    main()
