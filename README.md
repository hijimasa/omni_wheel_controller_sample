# omni_wheel_controller_sample

This is sample packages for [omni_wheel_controller](https://github.com/hijimasa/omni_wheel_controller).

## Usage

1. clone this repository to your work space
   ```
   cd <your_workspace_dir>/src
   git clone https://github.com/hijimasa/omni_wheel_controller_sample.git
   ```

2. build an environment with Dockerfile
   ```
   mkdir <your_workspace_dir>/../docker
   cp <your_workspace_dir>/src/omni_wheel_controller_sample/Dockerfile <your_workspace_dir>/../docker
   cd <your_workspace_dir>/../docker
   docker build --rm -t <your_docker_image_tag> .
   ```

3. launch your docker container
   ```
   cd <your_workspace_dir>/../docker
   docker run -it --rm --net host \
        --privileged -v /dev/bus/usb:/dev/bus/usb \
        --env="DISPLAY" \
        -v $HOME/.Xauthority:/root/.Xauthority:rw \
        -v /tmp/.X11-unix:/tmp/.X11-unix \
	--workdir="/root/colcon_ws" \
        --volume="$(pwd)/../colcon_ws:/root/colcon_ws" \
	irlab-ros2-image:latest
   ```

4. build program
   ```
   source /opt/ros/humble/setup.bash
   colcon build
   source install/setup.bash
   ```

5. run sample_robot with gazebo
   ```
   ros2 launch sample_robot_sim sample_robot_spawn.launch.py
   ```
