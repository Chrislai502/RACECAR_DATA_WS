from launch import LaunchDescription
from launch.conditions import IfCondition
from launch_ros.actions import Node
from launch.substitutions import LaunchConfiguration
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from ament_index_python.packages import get_package_share_directory
import launch_ros.actions
import os
import yaml
from launch.substitutions import EnvironmentVariable, TextSubstitution
import pathlib
import launch.actions
from launch.actions import DeclareLaunchArgument, SetLaunchConfiguration

def generate_launch_description():
    print("Share Directory:")
    print()
    share_dir = get_package_share_directory('racecar_utils')
    launch_dir = os.path.join(share_dir, 'launch')
    urdf = os.path.join(launch_dir, 'av21.urdf')
    rviz_path = os.path.join(launch_dir, 'lidar_tf.rviz')
    param_path = os.path.join(get_package_share_directory('perception_evaluation'), "params.yaml")

    with open(urdf, 'r') as infp:
        robot_desc = infp.read()

    arg_list = []
    ego_topic=LaunchConfiguration("ego_topic")
    opp_topic=LaunchConfiguration("opp_topic")

    ego_topic_arg = DeclareLaunchArgument("ego_topic", default_value="", description="topic name for ego odometry")
    opp_topic_arg = DeclareLaunchArgument("opp_topic", default_value="", description="topic name for opp odometry")
    
    use_sim_time=DeclareLaunchArgument("use_sim_time", default_value="false")
    param_arg = DeclareLaunchArgument('param_path', default_value="default_value", description='Param Path')
    update_param_arg = SetLaunchConfiguration('param_path', TextSubstitution(text=param_path))

    arg_list.append(use_sim_time)
    arg_list.append(ego_topic_arg)
    arg_list.append(opp_topic_arg)
    arg_list.append(param_arg)
    arg_list.append(update_param_arg)

    node_list= []

    # launch rosbag node
    # param_path = "/home/group1tracker/race_common/src/perception/IAC_Perception/src/perception_evaluation/perception_evaluation/params.yaml"



    with open(param_path, 'r') as file:
        params = yaml.safe_load(file)
        print("BAGPATH")
        print(f"{params['rosbag_info']['BAG_FILE_PATH']}")
        try:
            bag_file_path = params["rosbag_info"]["BAG_FILE_PATH"]
        except:
            bag_file_path = "/home/group1tracker/racecar_ws/data/RACECAR-ROS2/S6/T-MULTI-FAST-POLI"
        with open(bag_file_path + "/metadata.yaml", 'r') as file2:
            meta_yaml = yaml.safe_load(file2)
            params["rosbag_info"]["START_TIME"] = meta_yaml["rosbag2_bagfile_information"]["starting_time"]["nanoseconds_since_epoch"]
    with open(param_path, 'w') as file:
        yaml.dump(params, file)
    
    node_list.append(
        launch.actions.ExecuteProcess(
            cmd=['ros2', 'bag', 'play', bag_file_path, "--clock", "100.0"],
            name = "player"
        )
    )
    

    node_list.append(Node(
        package='racecar_utils',
        executable='odom_to_tf_node',
        name='odom_to_tf',
        remappings=[("odom_ego", ego_topic),
                    ("odom_opp", opp_topic)],
        parameters=[{use_sim_time.name: LaunchConfiguration(use_sim_time.name)}],
    ))

    node_list.append(Node(
    package='robot_state_publisher',
    executable='robot_state_publisher',
    name="robot_state_publisher",
    parameters=[{
        'publish_frequency': 1.0,
        'ignore_timestamp': False,
        'use_tf_static': True,
        'robot_description': robot_desc,
    }]
    ))
    # Launch rviz2 Node 
    node_list.append(Node(
            package    = 'rviz2',
            namespace  = 'lead',
            executable = 'rviz2',
            name       = 'rviz2',
            arguments  = ['-d' + str(rviz_path)] 
    )),

    # Launch Perception Node 
    node_list.append(
        launch.actions.ExecuteProcess(
            cmd=['ros2', 'launch', 'autonomy_launch', "perception.launch.py"],
            name = "perception_launcher"
        )
    )

    # Launch Validation node:
    node_list.append(Node(
        package    = 'perception_evaluation',
        # namespace  = 'lead',
        executable = 'validation_node',
        name       = 'validation',
        # arguments  = ['-d' + str(param_path)] 
        parameters = [{'param_yaml_path': LaunchConfiguration('param_path')}]
    ))


    return LaunchDescription(arg_list+node_list)
