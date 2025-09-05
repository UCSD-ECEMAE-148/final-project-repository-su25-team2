import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from roboflowoak import RoboflowOak
import time

class GestureControlCameraNode(Node):
    def __init__(self):
        super().__init__('gesture_control_camera_node')

        # Publisher for detected gestures
        self.gesture_pub = self.create_publisher(String, '/gestures', 10)
    
        # Init RoboflowOak
        self.rf = RoboflowOak(
            model="detect_handgestures-m8g8e",
            confidence=0.45,
            overlap=0.5,
            version="1",
            api_key="tC2EnrdOAYm1wteAYNe6",
            rgb=True,
            depth=True,
            device=None,
            blocking=True
        )

        # Run inference every 0.2s (20 Hz)
        self.timer = self.create_timer(0.1, self.run_inference)

        # Stability filter variables
        self.last_detected = None
        self.count = 0
        self.required_repeats = 5  # must see same gesture this many times

    def run_inference(self):
        t0 = time.time()
        result, frame, raw_frame, depth = self.rf.detect()
        predictions = result["predictions"]

        fps = 1.0 / (time.time() - t0)
        self.get_logger().info(f"FPS: {fps:.2f}")

        # Extract first gesture label (or none if no detection)
        label = predictions[0].json()['class'] if predictions else "none"
        self.get_logger().info(f"Detected Gesture: {label}")

        # Stability check
        if label == self.last_detected and label != "none":
            if self.count != self.required_repeats:
                self.count += 1
            else:
                self.count = 0
        else:
            self.count = 1
            self.last_detected = label

        # Only publish if detected consistently enough
        if self.count >= self.required_repeats:
            msg = String()
            msg.data = label
            self.gesture_pub.publish(msg)
            self.get_logger().info(f"Published stable gesture: {label}")
            self.count = 0  # reset after publishing


def main(args=None):
    rclpy.init(args=args)
    node = GestureControlCameraNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()
