import math

import rclpy
from rclpy.node import Node

from sensor_msgs.msg import LaserScan
from navigation_msgs.msg import ObstacleState


class ObstacleAvoidance(Node):

    def __init__(self):
        super().__init__("obstacle_avoidance_node")

        # =========================================================
        # Parameters
        # =========================================================

        self.declare_parameter(
            "scan_topic",
            "/scan"
        )

        self.declare_parameter(
            "front_angle_deg",
            30.0
        )

        self.declare_parameter(
            "front_stop_distance",
            0.80
        )

        self.declare_parameter(
            "front_slow_distance",
            1.50
        )

        self.declare_parameter(
            "scan_timeout",
            0.30
        )

        # =========================================================
        # Read parameters
        # =========================================================

        self.scan_topic = self.get_parameter(
            "scan_topic"
        ).value

        self.front_angle_deg = self.get_parameter(
            "front_angle_deg"
        ).value

        self.front_stop_distance = self.get_parameter(
            "front_stop_distance"
        ).value

        self.front_slow_distance = self.get_parameter(
            "front_slow_distance"
        ).value

        self.scan_timeout = self.get_parameter(
            "scan_timeout"
        ).value

        self.front_angle_rad = math.radians(
            self.front_angle_deg
        )

        # =========================================================
        # Internal state
        # =========================================================

        self.latest_scan = None
        self.last_scan_time = None

        # =========================================================
        # Subscriber
        # =========================================================

        self.scan_subscriber = self.create_subscription(
            LaserScan,
            self.scan_topic,
            self.scan_callback,
            10
        )

        # =========================================================
        # Publisher
        # =========================================================

        self.publisher = self.create_publisher(
            ObstacleState,
            "/obstacle_state",
            10
        )

        # =========================================================
        # Processing timer
        # =========================================================

        self.timer = self.create_timer(
            0.1,
            self.process_scan
        )

        # =========================================================
        # Startup information
        # =========================================================

        self.get_logger().info(
            "Obstacle Avoidance Node Started"
        )

        self.get_logger().info(
            f"Subscribed to: {self.scan_topic}"
        )

        self.get_logger().info(
            f"Front sector: +/- {self.front_angle_deg:.1f} degrees"
        )

        self.get_logger().info(
            f"Stop distance: {self.front_stop_distance:.2f} m"
        )

        self.get_logger().info(
            f"Slow distance: {self.front_slow_distance:.2f} m"
        )

        self.get_logger().info(
            f"Scan timeout: {self.scan_timeout:.2f} s"
        )

    # =============================================================
    # LaserScan callback
    # =============================================================

    def scan_callback(self, scan_msg):

        self.latest_scan = scan_msg

        self.last_scan_time = self.get_clock().now()

    # =============================================================
    # Main processing loop
    # =============================================================

    def process_scan(self):

        msg = ObstacleState()

        # ---------------------------------------------------------
        # No scan received
        # ---------------------------------------------------------

        if self.latest_scan is None:

            msg.state = "NO_SCAN"
            msg.distance = 0.0

            self.publisher.publish(msg)

            return

        # ---------------------------------------------------------
        # Check scan age
        # ---------------------------------------------------------

        now = self.get_clock().now()

        scan_age = (
            now - self.last_scan_time
        ).nanoseconds / 1e9

        if scan_age > self.scan_timeout:

            msg.state = "NO_SCAN"
            msg.distance = 0.0

            self.publisher.publish(msg)

            return

        # ---------------------------------------------------------
        # Find closest valid obstacle in front sector
        # ---------------------------------------------------------

        closest_distance = self.get_front_distance(
            self.latest_scan
        )

        # ---------------------------------------------------------
        # No valid obstacle in front sector
        # ---------------------------------------------------------

        if closest_distance is None:

            msg.state = "CLEAR"
            msg.distance = 99.0

            self.publisher.publish(msg)

            return

        # ---------------------------------------------------------
        # Determine obstacle state
        # ---------------------------------------------------------

        if closest_distance <= self.front_stop_distance:

            msg.state = "BLOCKED"

        elif closest_distance <= self.front_slow_distance:

            msg.state = "CAUTION"

        else:

            msg.state = "CLEAR"

        msg.distance = float(closest_distance)

        self.publisher.publish(msg)

    # =============================================================
    # Find closest valid range in front +/- angle
    # =============================================================

    def get_front_distance(self, scan):

        closest_distance = None

        angle = scan.angle_min

        for range_value in scan.ranges:

            # -----------------------------------------------------
            # Normalize angle to [-pi, pi]
            #
            # This is important because your N10P publishes:
            #
            # angle_min = 0
            # angle_max = 2*pi
            #
            # Therefore the front sector is split across the
            # beginning/end of the ranges array.
            # -----------------------------------------------------

            normalized_angle = math.atan2(
                math.sin(angle),
                math.cos(angle)
            )

            # -----------------------------------------------------
            # Check whether measurement is in front +/- 30 degrees
            # -----------------------------------------------------

            if abs(normalized_angle) <= self.front_angle_rad:

                # -------------------------------------------------
                # Reject NaN and infinity
                # -------------------------------------------------

                if not math.isfinite(range_value):

                    angle += scan.angle_increment
                    continue

                # -------------------------------------------------
                # Reject invalid minimum/maximum ranges
                # -------------------------------------------------

                if range_value <= scan.range_min:

                    angle += scan.angle_increment
                    continue

                if range_value >= scan.range_max:

                    angle += scan.angle_increment
                    continue

                # -------------------------------------------------
                # Keep closest valid obstacle
                # -------------------------------------------------

                if (
                    closest_distance is None
                    or range_value < closest_distance
                ):

                    closest_distance = range_value

            angle += scan.angle_increment

        return closest_distance


def main(args=None):

    rclpy.init(args=args)

    node = ObstacleAvoidance()

    try:

        rclpy.spin(node)

    except KeyboardInterrupt:

        pass

    finally:

        node.destroy_node()

        rclpy.shutdown()


if __name__ == "__main__":

    main()
