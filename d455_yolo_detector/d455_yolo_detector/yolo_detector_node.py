##!/usr/bin/env python3

import rclpy
from rclpy.node import Node

from sensor_msgs.msg import Image

from vision_msgs.msg import (
    Detection2DArray,
    Detection2D,
    ObjectHypothesisWithPose,
    BoundingBox2D
)

from cv_bridge import CvBridge

from ultralytics import YOLO

import cv2
import torch


from rclpy.qos import (
    QoSProfile,
    ReliabilityPolicy,
    HistoryPolicy
)



class YOLODetectorNode(Node):

    def __init__(self):

        super().__init__('yolo_detector')


        # ==========================
        # Parameters
        # ==========================

        self.declare_parameter(
            "model_path",
            "yolov8n.pt"
        )


        self.declare_parameter(
            "confidence_threshold",
            0.5
        )


        self.declare_parameter(
            "device",
            "cpu"
        )


        model_path = self.get_parameter(
            "model_path"
        ).value


        self.conf_threshold = self.get_parameter(
            "confidence_threshold"
        ).value


        self.device = self.get_parameter(
            "device"
        ).value



        # ==========================
        # Load YOLO
        # ==========================

        self.get_logger().info(
            "Loading YOLO model..."
        )


        self.model = YOLO(
            model_path
        )


        self.model.to(
            self.device
        )


        self.get_logger().info(
            f"YOLO loaded: {model_path} on {self.device}"
        )



        # ==========================
        # CV Bridge
        # ==========================

        self.bridge = CvBridge()



        # ==========================
        # QoS for RealSense
        # ==========================

        qos = QoSProfile(

            history=HistoryPolicy.KEEP_LAST,

            depth=10,

            reliability=ReliabilityPolicy.BEST_EFFORT

        )



        # ==========================
        # Subscribers
        # ==========================

        self.image_sub = self.create_subscription(

            Image,

            "/camera/camera/color/image_raw",

            self.image_callback,

            qos

        )



        # ==========================
        # Publishers
        # ==========================

        self.detection_pub = self.create_publisher(

            Detection2DArray,

            "/yolo/detections_2d",

            10

        )


        self.debug_pub = self.create_publisher(

            Image,

            "/yolo/debug_image",

            10

        )


        self.get_logger().info(
            "YOLO detector ready"
        )



    def image_callback(self,msg):

        try:

            frame = self.bridge.imgmsg_to_cv2(

                msg,

                desired_encoding="bgr8"

            )


        except Exception as e:

            self.get_logger().error(

                f"CV Bridge error: {e}"

            )

            return



        try:

            results = self.model(

                frame,

                verbose=False,

                conf=self.conf_threshold

            )


        except Exception as e:

            self.get_logger().error(

                f"YOLO inference error: {e}"

            )

            return



        detections = Detection2DArray()

        detections.header = msg.header



        annotated = frame.copy()



        for result in results:


            if result.boxes is None:

                continue



            for box in result.boxes:


                confidence = float(

                    box.conf[0].item()

                )


                if confidence < self.conf_threshold:

                    continue



                class_id = int(

                    box.cls[0].item()

                )


                class_name = str(

                    self.model.names[class_id]

                )



                x1,y1,x2,y2 = (

                    box.xyxy[0]

                    .cpu()

                    .numpy()

                    .astype(int)

                )



                detection = Detection2D()


                detection.header = msg.header



                bbox = BoundingBox2D()



                # IMPORTANT:
                # ROS2 Jazzy requires float64

                bbox.center.position.x = float(

                    (x1+x2)/2.0

                )


                bbox.center.position.y = float(

                    (y1+y2)/2.0

                )


                bbox.size_x = float(

                    x2-x1

                )


                bbox.size_y = float(

                    y2-y1

                )



                detection.bbox = bbox



                hypothesis = ObjectHypothesisWithPose()



                hypothesis.hypothesis.class_id = (

                    class_name

                )


                hypothesis.hypothesis.score = float(

                    confidence

                )


                detection.results.append(

                    hypothesis

                )


                detections.detections.append(

                    detection

                )



                # Draw debug

                cv2.rectangle(

                    annotated,

                    (x1,y1),

                    (x2,y2),

                    (0,255,0),

                    2

                )


                cv2.putText(

                    annotated,

                    f"{class_name} {confidence:.2f}",

                    (x1,y1-10),

                    cv2.FONT_HERSHEY_SIMPLEX,

                    0.6,

                    (0,255,0),

                    2

                )



        # Publish detections

        self.detection_pub.publish(

            detections

        )



        # Publish debug image

        debug = self.bridge.cv2_to_imgmsg(

            annotated,

            encoding="bgr8"

        )


        debug.header = msg.header


        self.debug_pub.publish(

            debug

        )



def main(args=None):

    rclpy.init(args=args)


    node = YOLODetectorNode()


    try:

        rclpy.spin(node)


    except KeyboardInterrupt:

        pass


    finally:

        node.destroy_node()

        rclpy.shutdown()



if __name__ == "__main__":

    main()
