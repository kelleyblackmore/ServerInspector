"""
System information collector for ServerInspect.
"""

import os
import platform
import logging
import socket
from datetime import datetime

logger = logging.getLogger("serverinspect")


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

    # Basic information that should work on any system
    try:
        # Get hostname
        info["hostname"] = runner.run_command("hostname").strip()

        # Get kernel and OS info
        uname_result = runner.run_command("uname -a").strip()
        info["uname"] = uname_result

        # Try to get OS release information
        if runner.file_exists("/etc/os-release"):
            os_release = runner.run_command("cat /etc/os-release")
            info["os_release"] = parse_os_release(os_release)

        # CPU information
        if runner.file_exists("/proc/cpuinfo"):
            cpu_info = runner.run_command("cat /proc/cpuinfo")
            info["cpu"] = parse_cpuinfo(cpu_info)

        # Memory information
        if runner.file_exists("/proc/meminfo"):
            mem_info = runner.run_command("cat /proc/meminfo")
            info["memory"] = parse_meminfo(mem_info)

        # Disk usage
        df_output = runner.run_command("df -h")
        info["disk_usage"] = parse_df_output(df_output)

        # Running processes count
        ps_count = runner.run_command("ps aux | wc -l")
        info["process_count"] = int(ps_count.strip()) - 1  # Subtract header line

        # Uptime
        uptime_output = runner.run_command("uptime")
        info["uptime"] = uptime_output.strip()

        # Collect additional information on the local system
        if runner.__class__.__name__ == "LocalRunner":
            local_info = collect_local_system_info()
            info.update(local_info)

    except Exception as e:
        logger.error(f"Error collecting system information: {str(e)}")
        info["error"] = str(e)

    # Add timestamp
    info["timestamp"] = datetime.now().isoformat()

    return info


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

        # Network information
        info["network"] = {
            "hostname": socket.gethostname(),
            "ip_address": socket.gethostbyname(socket.gethostname()),
        }

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
