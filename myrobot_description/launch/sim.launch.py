"""Launch Gazebo simulation, AMCL localization, and Nav2 stack for AMR robot."""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():
    """Generate launch description for simulation and autonomous navigation."""
    pkg_path = get_package_share_directory('myrobot_description')
    urdf_file = os.path.join(pkg_path, 'urdf', 'robot.urdf')
    world_file = os.path.join(pkg_path, 'worlds', 'my_world.sdf')
    nav2_params = os.path.join(pkg_path, 'config', 'nav2_params.yaml')
    map_file = os.path.join(pkg_path, 'maps', 'my_map.yaml')
    rviz_config = os.path.join(pkg_path, 'config', 'slam.rviz')
    bt_xml = os.path.join(pkg_path, 'config', 'navigate_to_pose.xml')

    with open(urdf_file, 'r') as f:
        robot_desc = f.read()

    # --- Gazebo ---
    gz_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('ros_gz_sim'),
                'launch',
                'gz_sim.launch.py'
            )
        ),
        launch_arguments={'gz_args': f'-r {world_file}'}.items()
    )

    # --- Robot State Publisher ---
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': robot_desc,
            'use_sim_time': True
        }]
    )

    # --- Spawn Robot ---
    spawn_robot = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-topic', 'robot_description',
            '-name', 'my_robot',
            '-z', '0.44'
        ],
        output='screen'
    )

    # --- ROS-GZ Bridges ---
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
        arguments=[
            '/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan',
        ],
        parameters=[{'override_frame_id': 'laser_frame'}],
        output='screen'
    )

    # --- Map Server ---
    map_server = Node(
        package='nav2_map_server',
        executable='map_server',
        name='map_server',
        output='screen',
        parameters=[{
            'use_sim_time': True,
            'yaml_filename': map_file
        }]
    )

    # --- AMCL ---
    amcl = Node(
        package='nav2_amcl',
        executable='amcl',
        name='amcl',
        output='screen',
        parameters=[nav2_params]
    )

    # --- Lifecycle Manager for localization ---
    lifecycle_manager_localization = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_localization',
        output='screen',
        parameters=[{
            'use_sim_time': True,
            'autostart': True,
            'node_names': ['map_server', 'amcl']
        }]
    )

    # --- Nav2 nodes launched directly ---
    controller_server = Node(
        package='nav2_controller',
        executable='controller_server',
        name='controller_server',
        output='screen',
        parameters=[nav2_params]
    )

    planner_server = Node(
        package='nav2_planner',
        executable='planner_server',
        name='planner_server',
        output='screen',
        parameters=[nav2_params]
    )

    behavior_server = Node(
        package='nav2_behaviors',
        executable='behavior_server',
        name='behavior_server',
        output='screen',
        parameters=[nav2_params]
    )

    bt_navigator = Node(
        package='nav2_bt_navigator',
        executable='bt_navigator',
        name='bt_navigator',
        output='screen',
        parameters=[
            nav2_params,
            {
                'default_nav_to_pose_bt_xml': bt_xml,
                'default_nav_through_poses_bt_xml': bt_xml
            }
        ]
    )

    smoother_server = Node(
        package='nav2_smoother',
        executable='smoother_server',
        name='smoother_server',
        output='screen',
        parameters=[nav2_params]
    )

    velocity_smoother = Node(
        package='nav2_velocity_smoother',
        executable='velocity_smoother',
        name='velocity_smoother',
        output='screen',
        parameters=[nav2_params]
    )

    waypoint_follower = Node(
        package='nav2_waypoint_follower',
        executable='waypoint_follower',
        name='waypoint_follower',
        output='screen',
        parameters=[nav2_params]
    )

    # --- Lifecycle Manager for navigation ---
    lifecycle_manager_navigation = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_navigation',
        output='screen',
        parameters=[{
            'use_sim_time': True,
            'autostart': False,
            'node_names': [
                'controller_server',
                'planner_server',
                'behavior_server',
                'bt_navigator',
                'smoother_server',
                'velocity_smoother',
                'waypoint_follower'
            ]
        }]
    )

    # --- RViz2 ---
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', rviz_config],
    )

    return LaunchDescription([
        gz_launch,
        robot_state_publisher,
        spawn_robot,
        bridge_core,
        bridge_scan,
        map_server,
        amcl,
        lifecycle_manager_localization,
        TimerAction(period=8.0, actions=[
            controller_server,
            planner_server,
            behavior_server,
            bt_navigator,
            smoother_server,
            velocity_smoother,
            waypoint_follower,
            lifecycle_manager_navigation,
        ]),
        rviz_node,
    ])
