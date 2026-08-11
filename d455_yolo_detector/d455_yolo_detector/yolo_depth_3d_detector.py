#!/usr/bin/env python3

import rclpy
from rclpy.node import Node

from sensor_msgs.msg import Image, CameraInfo

from vision_msgs.msg import (
    Detection2DArray,
    Detection3DArray,
    Detection3D
)

from cv_bridge import CvBridge

from message_filters import Subscriber
from message_filters import ApproximateTimeSynchronizer

import numpy as np


class YOLODepth3DNode(Node):

    def __init__(self):

        super().__init__(
            "yolo_depth_3d_detector"
        )

        self.bridge = CvBridge()


        self.det_sub = Subscriber(
            self,
            Detection2DArray,
            "/yolo/detections_2d"
        )


        self.depth_sub = Subscriber(
            self,
            Image,
            "/camera/camera/aligned_depth_to_color/image_raw"
        )


        self.info_sub = Subscriber(
            self,
            CameraInfo,
            "/camera/camera/color/camera_info"
        )


        self.sync = ApproximateTimeSynchronizer(
            [
                self.det_sub,
                self.depth_sub,
                self.info_sub
            ],
            10,
            0.2
        )


        self.sync.registerCallback(
            self.callback
        )


        self.pub = self.create_publisher(
            Detection3DArray,
            "/yolo/detections_3d",
            10
        )


        self.get_logger().info(
            "YOLO Depth 3D node started"
        )


    def get_depth(self, depth, u, v):

        h, w = depth.shape


        size = 5


        x1 = max(
            0,
            u-size
        )

        x2 = min(
            w,
            u+size
        )


        y1 = max(
            0,
            v-size
        )

        y2 = min(
            h,
            v+size
        )


        region = depth[y1:y2, x1:x2]


        valid = region[
            region > 0
        ]


        if len(valid) == 0:
            return None


        return float(
            np.median(valid)
        ) / 1000.0



    def callback(
        self,
        detections,
        depth_msg,
        camera_info
    ):


        fx = camera_info.k[0]
        fy = camera_info.k[4]

        cx = camera_info.k[2]
        cy = camera_info.k[5]


        depth = self.bridge.imgmsg_to_cv2(
            depth_msg,
            "passthrough"
        )


        output = Detection3DArray()

        output.header = detections.header


        count = 0


        for det in detections.detections:


            u = int(
                det.bbox.center.position.x
            )

            v = int(
                det.bbox.center.position.y
            )


            if (
                u < 0 or
                v < 0 or
                u >= depth.shape[1] or
                v >= depth.shape[0]
            ):
                continue



            z = self.get_depth(
                depth,
                u,
                v
            )


            if z is None:
                continue



            x = (
                (u-cx)
                *
                z
                /
                fx
            )


            y = (
                (v-cy)
                *
                z
                /
                fy
            )


            detection3d = Detection3D()

            detection3d.header = detections.header


            detection3d.bbox.center.position.x = x
            detection3d.bbox.center.position.y = y
            detection3d.bbox.center.position.z = z


            detection3d.results = det.results


            output.detections.append(
                detection3d
            )


            count += 1


        self.get_logger().info(
            f"3D detections: {count}"
        )


        self.pub.publish(
            output
        )



def main(args=None):

    rclpy.init(args=args)

    node = YOLODepth3DNode()

    rclpy.spin(node)

    node.destroy_node()

    rclpy.shutdown()



if __name__ == "__main__":

    main()
