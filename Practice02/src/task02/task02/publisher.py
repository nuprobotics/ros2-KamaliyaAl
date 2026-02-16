import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class Task02Publisher(Node):
    def __init__(self) -> None:
        super().__init__('task02_publisher')

        # параметр с дефолтом, но topic_name должен приходить из yaml
        self.declare_parameter('topic_name', '/spgc/receiver')
        self.declare_parameter('text', 'Hello, ROS2!')

        self._topic_name = self.get_parameter('topic_name').get_parameter_value().string_value
        self._text = self.get_parameter('text').get_parameter_value().string_value

        self._pub = self.create_publisher(String, self._topic_name, 10)

        self._timer = self.create_timer(0.5, self._on_timer)

        self.get_logger().info(f'Publishing to: {self._topic_name}')
        self.get_logger().info(f'Text: {self._text}')

    def _on_timer(self) -> None:
        msg = String()
        msg.data = self._text
        self._pub.publish(msg)


def main(args=None) -> None:
    rclpy.init(args=args)
    node = Task02Publisher()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()