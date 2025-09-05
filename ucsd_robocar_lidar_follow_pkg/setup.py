from setuptools import setup

package_name = 'ucsd_robocar_lidar_follow_pkg'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', [
           'launch/lidar_following_node.launch.py',
           'launch/gesture_action_node.launch.py',
           'launch/gesture_control_camera_node.launch.py',
        ]),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='root',
    maintainer_email='djnighti@ucsd.edu',
    description='Package for Lidar-based object following with VESC control',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'lidar_following_node = ucsd_robocar_lidar_follow_pkg.lidar_following_node:main',
            'gesture_action_node = ucsd_robocar_lidar_follow_pkg.gesture_action_node:main',
            'gesture_control_camera_node = ucsd_robocar_lidar_follow_pkg.gesture_control_camera_node:main',
        ],
    },
)
