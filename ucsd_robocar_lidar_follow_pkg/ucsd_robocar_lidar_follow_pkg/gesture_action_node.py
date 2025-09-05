import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from geometry_msgs.msg import Twist
from example_interfaces.srv import SetBool  # service type for toggle_follow
import time

class GestureActionNode(Node):
    def __init__(self):
        super().__init__('gesture_action_node')

        # Subscribe to gestures topic
        self.subscription = self.create_subscription(
            String,
            '/gestures',
            self.gesture_callback,
            10
        )
        self.twist_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.twist_cmd = Twist()

        # Service client for /toggle_follow
        self.cli = self.create_client(SetBool, 'toggle_follow')
        while not self.cli.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Waiting for toggle_follow service...')

        # Timeout control
        self.last_action_time = 0.0
        self.timeout = 0.5  # seconds

    def send_toggle_request(self, state: bool):
        req = SetBool.Request()
        req.data = state
        future = self.cli.call_async(req)
        future.add_done_callback(self.response_callback)

    def response_callback(self, future):
        try:
            response = future.result()
            self.get_logger().info(f"Service response: {response.message}")
        except Exception as e:
            self.get_logger().error(f"Service call failed: {e}")

    def gesture_callback(self, msg):
        current_time = time.time()
        if current_time - self.last_action_time < self.timeout:
            return  # still in cooldown

        gesture = msg.data
        self.get_logger().info(f"Received gesture: {gesture}")

        # Example gesture → service mapping
        if gesture == "open-hand":
            self.get_logger().info("START FOLLOWING")
            self.send_toggle_request(True)
        elif gesture == "closed-hand":
            self.get_logger().info("STOP FOLLOWING")
            self.send_toggle_request(False)
        elif gesture == "Vsign":
            self.get_logger().info("Turn-Around")
            #turn-around command
            self.twist_cmd.linear.x = 0.2
            self.twist_cmd.angular.z = 1.0  
            start_time = time.time()
            while time.time() - start_time < 2.0:  
                self.twist_pub.publish(self.twist_cmd)
            # stop after turning
            
            self.twist_cmd.linear.x = 0.0
            self.twist_cmd.angular.z = 0.0
            self.twist_pub.publish(self.twist_cmd)
        elif gesture == "thumbs_up":
            self.get_logger().info("MOVE RIGHT")
            twist.linear.x = 0.2
            twist.angular.z = 0.0

        else:
            self.get_logger().info("🤷 Gesture not mapped to any action")

        self.last_action_time = current_time


def main(args=None):
    rclpy.init(args=args)
    node = GestureActionNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()
