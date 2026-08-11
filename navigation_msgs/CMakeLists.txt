cmake_minimum_required(VERSION 3.8)

project(navigation_msgs)

find_package(ament_cmake REQUIRED)
find_package(rosidl_default_generators REQUIRED)

rosidl_generate_interfaces(${PROJECT_NAME}

msg/HumanState.msg
msg/ObstacleState.msg
msg/NavigationCommand.msg
msg/Position.msg

)

ament_export_dependencies(rosidl_default_runtime)

ament_package()
