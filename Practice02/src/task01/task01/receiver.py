import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class Receiver(Node):
    def __init__(self) -> None:
        super().__init__('receiver')
        self._sub = self.create_subscription(
            String,
            '/spgc/sender',
            self._on_msg,
            10
        )

    def _on_msg(self, msg: String) -> None:
        self.get_logger().info(msg.data)


def main(args=None) -> None:
    rclpy.init(args=args)
    node = Receiver()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()