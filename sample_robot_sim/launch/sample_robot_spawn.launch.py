import os
import math

from ament_index_python.packages import get_package_share_directory


from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, IncludeLaunchDescription
from launch.actions import RegisterEventHandler
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration

from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

import xacro

ROBOT1_START_POSITION    = [0.0, 0.0, 0.0]
ROBOT1_START_YAW = 0.0
def generate_launch_description():
    # Launch Arguments
    use_sim_time = LaunchConfiguration('use_sim_time', default=True)

    gazebo = IncludeLaunchDescription(
                PythonLaunchDescriptionSource([os.path.join(
                    get_package_share_directory('ros_gz_sim'), 'launch'), '/gz_sim.launch.py']),
                launch_arguments=[('gz_args', [' -r -v 4 empty.sdf'])]
             )

    sample_robot_description_path = os.path.join(
        get_package_share_directory('sample_robot_description'))

    xacro_file = os.path.join(sample_robot_description_path,
                              'robots',
                              'sample_robot.urdf.xacro')
    # xacroをロード
    doc = xacro.process_file(xacro_file, mappings={'use_sim' : 'true'})
    # xacroを展開してURDFを生成
    robot_desc = doc.toprettyxml(indent='  ')

    params = {'robot_description': robot_desc}

    rviz_config_file = os.path.join(sample_robot_description_path, 'config', 'sample_robot_description.rviz')
    
    node_robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[params]
    )

    gz_spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        output='screen',
        arguments=['-string', robot_desc,
                   '-name', 'sample_robot',
                   '-x', str(ROBOT1_START_POSITION[0]),
                   '-y', str(ROBOT1_START_POSITION[1]),
                   '-z', str(ROBOT1_START_POSITION[2]),
                   '-R', str(0.0),
                   '-P', str(0.0),
                   '-Y', str(ROBOT1_START_YAW),
                   '-allow_renaming', 'false'],
    )

    load_joint_state_controller = ExecuteProcess(
        cmd=['ros2', 'control', 'load_controller', '--set-state', 'active',
             'joint_state_broadcaster'],
        output='screen'
    )

    load_omni_wheel_controller = ExecuteProcess(
        cmd=['ros2', 'control', 'load_controller', '--set-state', 'active',
             'omni_wheel_controller'],
        output='screen'
    )

    # Bridge
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
                   '/camera_info@sensor_msgs/msg/CameraInfo@ignition.msgs.CameraInfo',
                   '/image_raw@sensor_msgs/msg/Image@ignition.msgs.Image',
                  ],
        output='screen'
    )

    velocity_converter = Node(
        package='velocity_pub',
        name='velocity_pub',
        executable='velocity_pub',
        remappings=[
            ('/cmd_vel_stamped', '/omni_wheel_controller/cmd_vel'),
        ],
    )

    rviz = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        output="log",
        arguments=["-d", rviz_config_file],
    )
    
    return LaunchDescription([
        RegisterEventHandler(
            event_handler=OnProcessExit(
                target_action=gz_spawn_entity,
                on_exit=[load_joint_state_controller],
            )
        ),
        RegisterEventHandler(
            event_handler=OnProcessExit(
               target_action=load_joint_state_controller,
               on_exit=[load_omni_wheel_controller],
            )
        ),
        gazebo,
        node_robot_state_publisher,
        gz_spawn_entity,
        bridge,
        velocity_converter,
        rviz,
    ]
    )
