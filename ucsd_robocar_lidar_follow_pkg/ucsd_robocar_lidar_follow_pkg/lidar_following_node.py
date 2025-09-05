import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan
from example_interfaces.srv import SetBool
import math


class FrontLidarFollower(Node):
    def __init__(self):
        super().__init__('front_lidar_follower')

        # Publisher for velocity commands
        self.twist_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.twist_cmd = Twist()

        # Subscribe to LiDAR
        self.create_subscription(LaserScan, '/scan', self.scan_callback, 10)

        # Motion parameters
        self.forward_speed = 0.3
        self.turn_speed = 1.0
        self.smoothing_factor = 0.2

        # Distance filtering
        self.min_distance_tolerance = 0.8
        self.max_distance_tolerance = 3.0

        # Angle window (degrees) for "front zone"
        self.front_angle_limit = 30  # ±30° around 0°

        self.prev_angular = 0.0

        # Service to start/stop following
        self.following = False
        self.srv = self.create_service(SetBool, 'toggle_follow', self.handle_follow_request)

    def handle_follow_request(self, request, response):
        self.following = request.data
        if self.following:
            response.message = "Following started"
        else:
            response.message = "Following stopped"
            self.stop_robot()
        response.success = True
        self.get_logger().info(response.message)
        return response

    def stop_robot(self):
        """Send a single stop command"""
        self.twist_cmd.linear.x = 0.0
        self.twist_cmd.angular.z = 0.0
        self.twist_pub.publish(self.twist_cmd)

    def scan_callback(self, msg: LaserScan):
        if not self.following:
            return  # do nothing if following is off

        scans_per_degree = len(msg.ranges) / 360.0

        closest_distance = float('inf')
        closest_angle = None

        # Only check ±front_angle_limit in front
        start_index = int((0 - self.front_angle_limit) * scans_per_degree) % len(msg.ranges)
        end_index = int((0 + self.front_angle_limit) * scans_per_degree) % len(msg.ranges)

        indices = range(start_index, end_index) if start_index < end_index else \
                  list(range(start_index, len(msg.ranges))) + list(range(0, end_index))

        for i in indices:
            distance = msg.ranges[i]
            if 0.1 < distance < self.max_distance_tolerance:
                angle_deg = (i / scans_per_degree)
                if angle_deg > 180:
                    angle_deg -= 360
                if abs(angle_deg) <= self.front_angle_limit:
                    if distance < closest_distance:
                        closest_distance = distance
                        closest_angle = -angle_deg

        # Stop if nothing detected
        if closest_distance == float('inf'):
            self.stop_robot()
            #debugging
            self.get_logger().info("No object in front zone, stopping")
            return

        # Stop if object is too close
        if 0 < closest_distance <= self.min_distance_tolerance:
            self.stop_robot()
           #Debugging
           # self.get_logger().info("Object too close, stopping")
            return

        # Turning
        target_angular = self.turn_speed * (closest_angle / self.front_angle_limit)
        self.twist_cmd.angular.z = (
            self.prev_angular + self.smoothing_factor * (target_angular - self.prev_angular)
        )
        self.prev_angular = self.twist_cmd.angular.z

        # Adjust forward speed
        angle_rad = math.radians(closest_angle)
        forward_factor = max(0.1, 1 - abs(angle_rad) / (math.pi / 2))
        self.twist_cmd.linear.x = self.forward_speed * forward_factor

        # Publish
        self.twist_pub.publish(self.twist_cmd)


       #DEBUGGING (UNCOMMENT TO SEE TWIST COMMANDS)
       # self.get_logger().info(
           # f"Following front object -> linear: {self.twist_cmd.linear.x:.2f}, "
           # f"angular: {self.twist_cmd.angular.z:.2f}, angle: {closest_angle:.1f}°"
       # )


def main(args=None):
    rclpy.init(args=args)
    node = FrontLidarFollower()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
