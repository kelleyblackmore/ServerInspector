"""
System information collector for serverinspector.
"""

import logging
import os
from datetime import datetime

logger = logging.getLogger("serverinspector")


def collect_system_info(runner):
    """
    Collect basic system information.

    Args:
        runner: A runner instance to execute commands

    Returns:
        dict: System information
    """
    logger.debug("Collecting system information")

    info = {}

    is_local = runner.__class__.__name__ == "LocalRunner"

    # Guard each step individually so one missing command (common when
    # running locally on Windows or a minimal system) doesn't abort the rest.
    def try_collect(key, func):
        try:
            value = func()
        except Exception as e:
            logger.warning(f"Could not collect {key}: {str(e)}")
            return
        if value is not None:
            info[key] = value

    def count_processes():
        if is_local:
            import psutil

            return len(psutil.pids())
        # Subtract header line
        return int(runner.run_command("ps aux | wc -l").strip()) - 1

    try_collect("hostname", lambda: runner.run_command("hostname").strip())
    try_collect("uname", lambda: runner.run_command("uname -a").strip())
    try_collect(
        "os_release",
        lambda: (
            parse_os_release(runner.run_command("cat /etc/os-release"))
            if runner.file_exists("/etc/os-release")
            else None
        ),
    )
    try_collect(
        "cpu",
        lambda: (
            parse_cpuinfo(runner.run_command("cat /proc/cpuinfo"))
            if runner.file_exists("/proc/cpuinfo")
            else None
        ),
    )
    try_collect(
        "memory",
        lambda: (
            parse_meminfo(runner.run_command("cat /proc/meminfo"))
            if runner.file_exists("/proc/meminfo")
            else None
        ),
    )
    try_collect("disk_usage", lambda: parse_df_output(runner.run_command("df -h")))
    try_collect("network", lambda: collect_network_info(runner))
    try_collect("process_count", count_processes)
    try_collect("uptime", lambda: runner.run_command("uptime").strip())

    # Collect additional information on the local system
    if is_local:
        info.update(collect_local_system_info())

    # Add timestamp
    info["timestamp"] = datetime.now().isoformat()

    return info


def collect_network_info(runner):
    """
    Collect network information.

    Args:
        runner: A runner instance to execute commands

    Returns:
        dict: Network information
    """
    network_info = {}

    try:
        # Get hostname and IP information
        hostname = runner.run_command("hostname").strip()
        network_info["hostname"] = hostname

        # Get IP addresses using ip command if available
        if runner.run_command("which ip 2>/dev/null || echo ''").strip():
            # Modern systems with 'ip' command
            # First get the list of interfaces
            iface_list = runner.run_command(
                "ip link show | grep -v 'link/' | grep -o '^[0-9]\\+: [^:]*' | cut -d' ' -f2"
            ).strip()
            interfaces = []

            # For each interface, get IP information
            for iface in iface_list.splitlines():
                iface = iface.strip()
                if not iface:
                    continue

                # Get IPv4 addresses for this interface
                ip_output = runner.run_command(
                    f"ip -4 addr show {iface} | grep inet"
                ).strip()
                if ip_output:
                    for line in ip_output.splitlines():
                        parts = line.strip().split()
                        if len(parts) >= 2 and parts[0] == "inet":
                            ip_cidr = parts[1]
                            ip_parts = ip_cidr.split("/")
                            interfaces.append(
                                {
                                    "interface": iface,
                                    "ip_address": ip_parts[0],
                                    "cidr": ip_cidr,
                                }
                            )

            network_info["interfaces"] = interfaces
        elif runner.run_command("which ifconfig 2>/dev/null || echo ''").strip():
            # Older systems with 'ifconfig' command
            ifconfig_output = runner.run_command("ifconfig").strip()
            network_info["interfaces"] = parse_ifconfig_output(ifconfig_output)

        # Get default gateway
        if runner.run_command("which ip 2>/dev/null || echo ''").strip():
            gateway_output = runner.run_command("ip route | grep default").strip()
            if gateway_output:
                parts = gateway_output.split()
                if len(parts) >= 3:
                    network_info["default_gateway"] = parts[2]

        # Get DNS servers
        if runner.file_exists("/etc/resolv.conf"):
            resolv_conf = runner.run_command("cat /etc/resolv.conf").strip()
            dns_servers = []
            for line in resolv_conf.splitlines():
                if line.startswith("nameserver"):
                    parts = line.split()
                    if len(parts) >= 2:
                        dns_servers.append(parts[1])
            if dns_servers:
                network_info["dns_servers"] = dns_servers

        # Check connectivity
        ping_result = runner.run_command(
            "ping -c 1 -W 1 8.8.8.8 2>/dev/null || echo 'Failed'"
        ).strip()
        network_info["internet_connectivity"] = "Failed" not in ping_result

    except Exception as e:
        logger.error(f"Error collecting network information: {str(e)}")
        network_info["error"] = str(e)

    return network_info


def parse_ip_output(ip_output):
    """
    Parse the output of the 'ip addr' command.

    Args:
        ip_output (str): Output of ip addr command

    Returns:
        list: List of interfaces with IP information
    """
    interfaces = []

    # Process each line with an IP address
    for line in ip_output.splitlines():
        parts = line.strip().split()
        if len(parts) >= 4:
            # Extract IP address
            ip_cidr = None
            for part in parts:
                if "/" in part and part[0].isdigit():
                    ip_cidr = part
                    break

            if not ip_cidr:
                continue

            # Try to extract interface name
            interface_name = "unknown"
            # The line should contain something like "inet 192.168.1.1/24 ... dev eth0"
            # Look for "dev" keyword followed by interface name
            for i, part in enumerate(parts):
                if part == "dev" and i + 1 < len(parts):
                    interface_name = parts[i + 1]
                    break

            # If we couldn't find via dev, try a different approach - check for scope
            if interface_name == "unknown":
                for i, part in enumerate(parts):
                    if part == "scope" and i > 1:
                        # Interface might be before scope
                        interface_name = parts[i - 2]
                        break

            ip_parts = ip_cidr.split("/")
            interfaces.append(
                {
                    "interface": interface_name,
                    "ip_address": ip_parts[0],
                    "cidr": ip_cidr,
                }
            )

    return interfaces


def parse_ifconfig_output(ifconfig_output):
    """
    Parse the output of the 'ifconfig' command.

    Args:
        ifconfig_output (str): Output of ifconfig command

    Returns:
        list: List of interfaces with IP information
    """
    interfaces = []
    current_interface = None

    lines = ifconfig_output.splitlines()
    for line in lines:
        line = line.strip()
        if line and not line.startswith(" "):
            # This is a new interface
            parts = line.split()
            if parts:
                current_interface = parts[0].rstrip(":")
        elif line.strip().startswith("inet ") and current_interface:
            # This line has IPv4 information
            parts = line.split()
            for i, part in enumerate(parts):
                if part == "inet" and i + 1 < len(parts):
                    ip_address = parts[i + 1]
                    if ip_address:
                        interface_info = {
                            "interface": current_interface,
                            "ip_address": ip_address,
                        }
                        # Look for netmask
                        for j, p in enumerate(parts):
                            if p in ["netmask", "mask"] and j + 1 < len(parts):
                                interface_info["netmask"] = parts[j + 1]
                                break
                        interfaces.append(interface_info)
                    break

    return interfaces


def collect_local_system_info():
    """
    Collect additional system information on the local system using psutil.

    Returns:
        dict: Additional system information
    """
    info = {}

    try:
        import psutil

        # CPU information
        info["cpu_percent"] = psutil.cpu_percent(interval=1)
        info["cpu_count"] = {
            "physical": psutil.cpu_count(logical=False),
            "logical": psutil.cpu_count(logical=True),
        }

        # Memory information
        mem = psutil.virtual_memory()
        info["memory_detailed"] = {
            "total": bytes_to_human_readable(mem.total),
            "available": bytes_to_human_readable(mem.available),
            "percent_used": mem.percent,
            "used": bytes_to_human_readable(mem.used),
            "free": bytes_to_human_readable(mem.free),
        }

        # Disk information
        disk_info = []
        for part in psutil.disk_partitions(all=False):
            if os.name == "nt":
                if "cdrom" in part.opts or part.fstype == "":
                    # Skip CD-ROM drives on Windows
                    continue
            usage = psutil.disk_usage(part.mountpoint)
            disk_info.append(
                {
                    "device": part.device,
                    "mountpoint": part.mountpoint,
                    "fstype": part.fstype,
                    "total": bytes_to_human_readable(usage.total),
                    "used": bytes_to_human_readable(usage.used),
                    "free": bytes_to_human_readable(usage.free),
                    "percent": usage.percent,
                }
            )
        info["disk_detailed"] = disk_info

        # Detailed network information if not already collected
        if "network" not in info:
            # Get network interfaces and stats
            net_io = psutil.net_io_counters(pernic=True)
            net_if_addrs = psutil.net_if_addrs()

            interfaces = []
            for iface, addrs in net_if_addrs.items():
                iface_info = {"interface": iface, "addresses": []}

                # Add addresses
                for addr in addrs:
                    addr_info = {"family": str(addr.family), "address": addr.address}
                    if addr.netmask:
                        addr_info["netmask"] = addr.netmask
                    if addr.broadcast:
                        addr_info["broadcast"] = addr.broadcast
                    iface_info["addresses"].append(addr_info)

                # Add IO statistics if available
                if iface in net_io:
                    iface_stats = net_io[iface]
                    iface_info["stats"] = {
                        "bytes_sent": bytes_to_human_readable(iface_stats.bytes_sent),
                        "bytes_recv": bytes_to_human_readable(iface_stats.bytes_recv),
                        "packets_sent": iface_stats.packets_sent,
                        "packets_recv": iface_stats.packets_recv,
                        "errin": iface_stats.errin,
                        "errout": iface_stats.errout,
                        "dropin": iface_stats.dropin,
                        "dropout": iface_stats.dropout,
                    }

                interfaces.append(iface_info)

            info["network_detailed"] = {"interfaces": interfaces}

            # Add default network connection info
            try:
                connections = psutil.net_connections()
                info["network_detailed"]["connection_count"] = len(connections)
                # Trying to get default gateway is complex with psutil, skipping for now
            except (psutil.AccessDenied, PermissionError):
                # This might require elevated privileges
                info["network_detailed"]["connection_count"] = "Access denied"

        # Boot time
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        info["boot_time"] = boot_time.isoformat()

    except ImportError:
        logger.warning("psutil not available, limited system information collected")
    except Exception as e:
        logger.error(f"Error collecting local system information: {str(e)}")

    return info


def parse_os_release(os_release_content):
    """
    Parse the /etc/os-release file content.

    Args:
        os_release_content (str): Content of /etc/os-release

    Returns:
        dict: Parsed OS release information
    """
    result = {}
    for line in os_release_content.splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            value = value.strip('"').strip("'")
            result[key] = value
    return result


def parse_cpuinfo(cpuinfo_content):
    """
    Parse the /proc/cpuinfo file content.

    Args:
        cpuinfo_content (str): Content of /proc/cpuinfo

    Returns:
        dict: Parsed CPU information
    """
    result = {}
    current_processor = {}
    processor_count = 0

    for line in cpuinfo_content.splitlines():
        if line.strip():
            if ":" in line:
                key, value = [part.strip() for part in line.split(":", 1)]
                if key == "processor":
                    # Starting a new processor section
                    if current_processor:
                        result[f"processor_{processor_count-1}"] = current_processor
                    processor_count += 1
                    current_processor = {key: value}
                else:
                    current_processor[key] = value

    # Add the last processor
    if current_processor:
        result[f"processor_{processor_count-1}"] = current_processor

    result["processor_count"] = processor_count

    # Add some summary information
    if processor_count > 0:
        sample_proc = result.get("processor_0", {})
        result["model_name"] = sample_proc.get("model name", "Unknown")
        result["vendor_id"] = sample_proc.get("vendor_id", "Unknown")

    return result


def parse_meminfo(meminfo_content):
    """
    Parse the /proc/meminfo file content.

    Args:
        meminfo_content (str): Content of /proc/meminfo

    Returns:
        dict: Parsed memory information
    """
    result = {}

    for line in meminfo_content.splitlines():
        if ":" in line:
            key, value = [part.strip() for part in line.split(":", 1)]
            if "kB" in value:
                # Convert from kB to MB and add both values
                kb_value = int(value.split()[0])
                mb_value = kb_value / 1024
                result[key] = f"{kb_value} kB ({mb_value:.2f} MB)"
            else:
                result[key] = value

    # Calculate some useful derived values
    if "MemTotal" in result and "MemFree" in result:
        total_kb = int(result["MemTotal"].split()[0])
        free_kb = int(result["MemFree"].split()[0])
        used_kb = total_kb - free_kb
        used_percent = (used_kb / total_kb) * 100 if total_kb > 0 else 0

        result["MemUsed"] = f"{used_kb} kB ({used_kb/1024:.2f} MB)"
        result["MemUsedPercent"] = f"{used_percent:.1f}%"

    return result


def parse_df_output(df_output):
    """
    Parse the output of the df -h command.

    Args:
        df_output (str): Output of df -h

    Returns:
        list: Parsed disk usage information
    """
    result = []

    lines = df_output.splitlines()
    if len(lines) <= 1:
        return result

    # Skip the header line
    for line in lines[1:]:
        parts = line.split()
        if len(parts) >= 6:  # Standard df -h output has 6 columns
            filesystem = parts[0]
            size = parts[1]
            used = parts[2]
            avail = parts[3]
            use_percent = parts[4]
            mounted_on = parts[5]

            result.append(
                {
                    "filesystem": filesystem,
                    "size": size,
                    "used": used,
                    "available": avail,
                    "use_percent": use_percent,
                    "mounted_on": mounted_on,
                }
            )

    return result


def bytes_to_human_readable(bytes_value):
    """
    Convert bytes to a human-readable string.

    Args:
        bytes_value (int): Value in bytes

    Returns:
        str: Human-readable string
    """
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if bytes_value < 1024 or unit == "TB":
            return f"{bytes_value:.2f} {unit}"
        bytes_value /= 1024
