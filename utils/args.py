import argparse
import os
from urllib.parse import urlparse

def validate_log_level(value: str) -> str:
    levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
    if value.upper() in levels:
        return value.upper()
    else:
        raise argparse.ArgumentTypeError(f"Invalid log level: {value}")

def validate_config_path(value: str) -> str:
    """
    Ensure config path exists, is a readable file, and looks like YAML.
    Returns the original path (expanded) so argparse can use it.
    """

    expanded = os.path.expanduser(value)

    if not os.path.exists(expanded):
        raise argparse.ArgumentTypeError(f"Config file not found: {expanded}")

    if not os.path.isfile(expanded):
        raise argparse.ArgumentTypeError(f"Config path is not a file: {expanded}")

    if not os.access(expanded, os.R_OK):
        raise argparse.ArgumentTypeError(f"Config file is not readable: {expanded}")

    _, ext = os.path.splitext(expanded.lower())
    if ext not in (".yml", ".yaml"):
        raise argparse.ArgumentTypeError("Config file must be .yml or .yaml")

    return expanded

def validate_port(value: str) -> int:
    try:
        port = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError("Port must be an integer")
    if not (1 <= port <= 65535):
        raise argparse.ArgumentTypeError("Port must be between 1 and 65535")
    return port

def validate_rpc_url(value: str) -> str:
    """Ensure the RPC is a valid http/https URL."""
    parsed = urlparse(value)
    if parsed.scheme not in ("http", "https"):
        raise argparse.ArgumentTypeError("RPC URL must start with http:// or https://")
    if not parsed.netloc:
        raise argparse.ArgumentTypeError("RPC URL missing hostname")
    return value

def parse_args():
    parser = argparse.ArgumentParser(
        description="Global arguments for the application",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--log-lvl",
        default="INFO",
        type=validate_log_level,
        help="Set the logging level [DEBUG, INFO, WARNING, ERROR]",
    )
    parser.add_argument(
        "--log-path",
        type=str,
        help="Path to the log file. If not provided, logs will not be stored",
        required=False,
    )
    parser.add_argument(
        "--config-path",
        type=validate_config_path,
        help="Config YAML path",
        default="config.yaml"
    )
    parser.add_argument(
        "--prometheus-host",
        type=str,
        default="127.0.0.1",
        help="Bind address for the /metrics HTTP server (use 0.0.0.0 to expose publicly)",
    )
    parser.add_argument(
        "--prometheus-port",
        type=validate_port,
        default=9101,
        help="Port for the /metrics HTTP server",
    )
    parser.add_argument(
        "--rpc-url",
        type=validate_rpc_url,
        help="RPC server http/s",
        default="https://rpc.monad.xyz:443"
    )
    parser.add_argument(
        "--token-price-update-interval",
        type=int,
        default=300,
        help="How often to refresh MON price (seconds)",
    )

    parser.add_argument(
        "--wallet-balance-update-interval",
        type=int,
        default=120,
        help="How often to refresh wallet balances (seconds)",
    )
    parser.add_argument(
        "--staking-update-interval",
        type=int,
        default=60,
        help="How often to refresh staking metrics (seconds)",
    )
    
    args = parser.parse_args()
    return args

args = parse_args()