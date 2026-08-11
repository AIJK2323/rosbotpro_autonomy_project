#!/usr/bin/env python3

import rclpy
from rclpy.node import Node

from d455_yolo_detector.msg import TrackedObjectArray
from navigation_msgs.msg import HumanState


class HumanBehavior(Node):

    def __init__(self):

        super().__init__("human_behavior_node")


        # Publisher
        self.state_pub = self.create_publisher(
            HumanState,
            "/human_state",
            10
        )


        # Subscriber
        self.tracked_sub = self.create_subscription(
            TrackedObjectArray,
            "/tracked_objects",
            self.tracked_callback,
            10
        )


        self.get_logger().info(
            "Human Behavior Node Started"
        )


    def tracked_callback(self, msg):

        closest_distance = None


        # Search only humans
        for obj in msg.objects:

            if obj.class_name == "person":

                distance = obj.position.z


                if closest_distance is None:

                    closest_distance = distance

                elif distance < closest_distance:

                    closest_distance = distance



        state = "CLEAR"


        if closest_distance is not None:


            if closest_distance < 1.5:

                state = "STOP"


            elif closest_distance < 3.0:

                state = "SLOW"



        output = HumanState()

        output.state = state


        if closest_distance is None:

            output.distance = 99.0

        else:

            output.distance = closest_distance


        self.state_pub.publish(output)


        self.get_logger().info(
            f"Human: {state}, Distance: {output.distance:.2f}m"
        )



def main(args=None):

    rclpy.init(args=args)

    node = HumanBehavior()

    rclpy.spin(node)


    node.destroy_node()

    rclpy.shutdown()



if __name__ == "__main__":

    main()
