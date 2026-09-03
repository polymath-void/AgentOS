import logging
from dataclasses import dataclass
from typing import Dict, Any

# Configure default logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

@dataclass
class NodeMetrics:
    """
    Dataclass representing performance and memory metrics for a node.
    """
    node_id: str
    cpu_usage_percent: float
    memory_throughput_mbps: float
    active_connections: int


class TelemetryLogger:
    """
    A telemetry module designed to log node performance and memory throughput.
    """

    def __init__(self, component_name: str = "NeuralAgentNetwork"):
        """
        Initializes the TelemetryLogger.

        Args:
            component_name (str): The name of the component for the logger.
        """
        self.logger = logging.getLogger(f"{component_name}.Telemetry")

    def log_node_performance(self, metrics: NodeMetrics) -> None:
        """
        Logs the performance metrics of a specific node.

        Args:
            metrics (NodeMetrics): The metrics data to log.
        """
        self.logger.info(
            f"Node Performance [{metrics.node_id}]: "
            f"CPU: {metrics.cpu_usage_percent:.2f}% | "
            f"Mem Throughput: {metrics.memory_throughput_mbps:.2f} MB/s | "
            f"Active Conns: {metrics.active_connections}"
        )

    def log_event(self, event_name: str, event_data: Dict[str, Any]) -> None:
        """
        Logs a custom telemetry event.

        Args:
            event_name (str): The name of the event.
            event_data (Dict[str, Any]): Additional data associated with the event.
        """
        self.logger.info(f"Telemetry Event: {event_name} | Data: {event_data}")
