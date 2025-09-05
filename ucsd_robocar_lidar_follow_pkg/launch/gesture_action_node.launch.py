from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='ucsd_robocar_lidar_follow_pkg',   
            executable='gesture_action_node',         
            name='gesture_action_node',               
            output='screen'
        )
    ])
