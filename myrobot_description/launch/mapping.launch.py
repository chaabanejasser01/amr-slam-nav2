"""Launch SLAM Toolbox mapping and Gazebo simulation for the AMR robot."""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():
    """Generate launch description for online SLAM mapping."""
    pkg_path = get_package_share_directory('myrobot_description')
    urdf_file = os.path.join(pkg_path, 'urdf', 'robot.urdf')
    world_file = os.path.join(pkg_path, 'worlds', 'my_world.sdf')
    slam_params = os.path.join(pkg_path, 'config', 'slam_toolbox_params.yaml')

    with open(urdf_file, 'r') as f:
        robot_desc = f.read()

    gz_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('ros_gz_sim'),
                'launch', 'gz_sim.launch.py'
            )
        ),
        launch_arguments={'gz_args': f'-r {world_file}'}.items()
    )

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': robot_desc, 'use_sim_time': True}]
    )

    spawn_robot = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=['-topic', 'robot_description', '-name', 'my_robot', '-z', '0.44'],
        output='screen'
    )

    bridge_core = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
            '/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist',
            '/odom@nav_msgs/msg/Odometry[gz.msgs.Odometry',
            '/tf@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V',
        ],
        output='screen'
    )

    bridge_scan = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=['/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan'],
        parameters=[{'override_frame_id': 'laser_frame'}],
        output='screen'
    )

    slam_node = Node(
        package='slam_toolbox',
        executable='async_slam_toolbox_node',
        name='slam_toolbox',
        output='screen',
        parameters=[slam_params],
    )

    return LaunchDescription([
        gz_launch,
        robot_state_publisher,
        spawn_robot,
        bridge_core,
        bridge_scan,
        slam_node,
    ])
