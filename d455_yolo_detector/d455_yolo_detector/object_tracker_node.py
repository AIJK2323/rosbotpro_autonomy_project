#!/usr/bin/env python3

import rclpy
from rclpy.node import Node

from vision_msgs.msg import Detection3DArray

from geometry_msgs.msg import Point, Vector3

from d455_interfaces.msg import (
    TrackedObject,
    TrackedObjectArray
)

import math
import time



class Track:

    def __init__(
        self,
        track_id,
        cls,
        confidence,
        x,
        y,
        z
    ):

        self.id = track_id

        self.class_name = cls

        self.confidence = confidence


        self.x = x
        self.y = y
        self.z = z


        self.prev_x = x
        self.prev_y = y
        self.prev_z = z


        self.vx = 0.0
        self.vy = 0.0
        self.vz = 0.0


        self.last_seen = time.time()

        self.age = 1



    def update(
        self,
        confidence,
        x,
        y,
        z
    ):

        dt = max(
            time.time() - self.last_seen,
            0.01
        )


        alpha = 0.7


        # velocity estimation

        self.vx = (x - self.prev_x) / dt
        self.vy = (y - self.prev_y) / dt
        self.vz = (z - self.prev_z) / dt



        # smoothing

        self.x = (
            alpha*x +
            (1-alpha)*self.x
        )

        self.y = (
            alpha*y +
            (1-alpha)*self.y
        )

        self.z = (
            alpha*z +
            (1-alpha)*self.z
        )


        self.prev_x = x
        self.prev_y = y
        self.prev_z = z


        self.confidence = confidence


        self.last_seen = time.time()

        self.age += 1





class ObjectTrackerNode(Node):


    def __init__(self):

        super().__init__(
            "object_tracker"
        )


        self.tracks=[]

        self.next_id=0


        self.max_distance=0.75

        self.timeout=2.0



        self.sub=self.create_subscription(

            Detection3DArray,

            "/yolo/detections_3d",

            self.callback,

            10

        )



        self.pub=self.create_publisher(

            TrackedObjectArray,

            "/tracked_objects",

            10

        )



        self.get_logger().info(
            "Object tracker started"
        )





    def distance(self,a,b):

        return math.sqrt(

            (a.x-b.x)**2 +

            (a.y-b.y)**2 +

            (a.z-b.z)**2

        )





    def callback(self,msg):


        detections=[]



        for det in msg.detections:


            x=float(
                det.bbox.center.position.x
            )

            y=float(
                det.bbox.center.position.y
            )

            z=float(
                det.bbox.center.position.z
            )


            if len(det.results):

                cls = (
                    det.results[0]
                    .hypothesis
                    .class_id
                )

                confidence=float(
                    det.results[0]
                    .hypothesis
                    .score
                )


            else:

                cls="unknown"

                confidence=0.0



            detections.append(

                (
                    cls,
                    confidence,
                    x,
                    y,
                    z
                )

            )




        for cls,confidence,x,y,z in detections:


            best=None

            best_dist=self.max_distance



            candidate=Track(

                -1,
                cls,
                confidence,
                x,
                y,
                z

            )



            for track in self.tracks:


                if track.class_name != cls:

                    continue


                d=self.distance(
                    candidate,
                    track
                )


                if d < best_dist:

                    best_dist=d

                    best=track





            if best:


                best.update(

                    confidence,

                    x,

                    y,

                    z

                )



            else:


                new_track=Track(

                    self.next_id,

                    cls,

                    confidence,

                    x,

                    y,

                    z

                )


                self.next_id += 1


                self.tracks.append(
                    new_track
                )






        # Remove old tracks

        now=time.time()


        self.tracks=[

            t for t in self.tracks

            if now-t.last_seen < self.timeout

        ]




        output=TrackedObjectArray()

        output.header=msg.header





        for track in self.tracks:


            obj=TrackedObject()


            obj.id=track.id


            obj.class_name=(
                track.class_name
            )


            obj.confidence=(
                track.confidence
            )



            obj.position=Point(

                x=track.x,

                y=track.y,

                z=track.z

            )



            obj.velocity=Vector3(

                x=track.vx,

                y=track.vy,

                z=track.vz

            )



            obj.state="tracked"



            output.objects.append(
                obj
            )



        self.pub.publish(
            output
        )






def main(args=None):

    rclpy.init(args=args)

    node=ObjectTrackerNode()

    rclpy.spin(node)


    node.destroy_node()

    rclpy.shutdown()



if __name__=="__main__":

    main()
