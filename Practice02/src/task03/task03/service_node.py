import rclpy
from rclpy.node import Node
from std_srvs.srv import Trigger


class Task03Node(Node):
    def __init__(self) -> None:
        super().__init__('task03_node')

        self.declare_parameter('service_name', '/trigger_service')
        self.declare_parameter('default_string', 'No service available')

        self._service_name = self.get_parameter('service_name').get_parameter_value().string_value
        self._default_string = self.get_parameter('default_string').get_parameter_value().string_value

        self._stored_string = self._default_string

        # client to external service
        self._client = self.create_client(Trigger, '/spgc/trigger')

        # our service
        self._server = self.create_service(Trigger, self._service_name, self._on_service_call)

        # call /spgc/trigger once at startup (non-blocking-ish via timer)
        self._called_once = False
        self._startup_timer = self.create_timer(0.1, self._try_call_external_once)

        self.get_logger().info(f'Providing service: {self._service_name}')
        self.get_logger().info('Will call external service: /spgc/trigger')

    def _try_call_external_once(self) -> None:
        if self._called_once:
            return
        self._called_once = True
        self._startup_timer.cancel()

        if not self._client.wait_for_service(timeout_sec=1.0):
            self._stored_string = self._default_string
            self.get_logger().warn("Service /spgc/trigger not available. Using default_string.")
            return

        req = Trigger.Request()
        future = self._client.call_async(req)
        future.add_done_callback(self._on_external_done)

    def _on_external_done(self, future) -> None:
        try:
            resp = future.result()
        except Exception as exc:  # noqa: BLE001
            self._stored_string = self._default_string
            self.get_logger().warn(f'External call failed, using default_string. Error: {exc}')
            return

        # store returned message (even if success=False, message still exists)
        self._stored_string = resp.message
        self.get_logger().info(f"Stored string from /spgc/trigger: '{self._stored_string}'")

    def _on_service_call(self, request: Trigger.Request, response: Trigger.Response) -> Trigger.Response:
        response.success = True
        response.message = self._stored_string
        return response


def main(args=None) -> None:
    rclpy.init(args=args)
    node = Task03Node()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()