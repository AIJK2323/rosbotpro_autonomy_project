# ROS 2 Autonomous Navigation Stack for ROSBOT Pro 2

N10P 2D LiDAR + D455 Human Perception + Path Following

## Hardware Required for the System:
1.  LSLIDAR N10P
2.  Intel Realsense D455
3.  Rosbot Pro 2 (Ackermann-style robot)

## Project Node Structure
1. Path Follower - Node for path-based navigation
2. Human Behaviour - Node for human detection and tracking
3. Obstacle avoidance -  Node for obstacle avoidance using the 2D Planar Lidar
4. Navigation Manager - Node for command prioritization
5. Navigation to Rosbot - Node that converts the navigation into ```bash /cmd_vel```

The architecture is intentionally made to separate perception, decision-making, and robot control.

## N10P ```bash /scan```

The N10P publishes ```bash /scan```

 This provides the information of: 

 ```bash
header.frame_id
angle_min
angle_max
angle_increment
range_min
range_max
ranges intensities
```
---

## Obstacle Avoidance Node

Package:

obstacle_avoidance

Executable:

obstacle_avoidance_node

Run with:

ros2 run obstacle_avoidance obstacle_avoidance_node

The node subscribes to:

/scan

and publishes:

/obstacle_state

Message type:

navigation_msgs/msg/ObstacleState

The message contains:

string state
float32 distance

The obstacle avoidance node is responsible for converting raw LiDAR measurements into a simplified navigation state.

---


## Obstacle States

CLEAR

Indicates that no obstacle has been detected inside the configured danger region.

Example:

state: CLEAR
distance: 4.5

The navigation manager is allowed to continue normal navigation.

---

CAUTION

Indicates that an obstacle is approaching the configured caution distance.

Example:

state: CAUTION
distance: 1.2

The navigation manager reduces the forward velocity while maintaining the path follower's steering command.

---

BLOCKED

Indicates that an obstacle is inside the configured stopping distance.

Example:

state: BLOCKED
distance: 0.6

The navigation manager generates:

linear_velocity: 0.0
angular_velocity: 0.0
state: STOP

The robot therefore stops.

---

NO_SCAN

Indicates that a valid LiDAR measurement is unavailable.

This is treated as a safety condition.

The navigation manager stops the robot instead of assuming the environment is clear.

---

## Parameters Used: 

Front sector: ±30°
Stop distance: 0.80 m
Slow distance: 1.50 m
Scan timeout: 0.30 s

Therefore:

distance <= 0.80 m = BLOCKED

and approximately:

0.80 m < distance <= 1.50 m = CAUTION

while:

distance > 1.50 m = CLEAR

The exact behavior depends on the implementation of the current obstacle avoidance node.

---

## Navigation Manager

Package:

navigation_manager

Executable:

navigation_manager_node

Run with:

ros2 run navigation_manager navigation_manager_node

The navigation manager is the central decision-making node.

It subscribes to:

/path_command
/human_command
/obstacle_state

and publishes:

/navigation_command

The important architectural change for the N10P integration is that the navigation manager now consumes:

/obstacle_state

using:

navigation_msgs/msg/ObstacleState

rather than expecting an obstacle

---

## Navigation Priority 

The current priority is:

1. Obstacle Safety
2. Human Behavior
3. Path Following
4. STOP if no valid command exists

This means obstacle safety has the highest priority.


