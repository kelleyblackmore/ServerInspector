# serverinspector Examples

This directory contains examples of serverinspector configurations and output formats.

## Configuration Examples

### Basic Test

`configs/basic_test.yaml` - A simple configuration demonstrating core functionality.

### Comprehensive Test

`configs/comprehensive_test.yaml` - A complete example showcasing all available
test types and options.

### Variable Test

`configs/variable_test.yaml` - Demonstrates how to use variable substitution in
your configuration files.

### SSH Test

`configs/ssh_test.yaml` - Shows how to configure tests for remote servers via SSH.

### System Info

`configs/system_info.yaml` - Configuration focused on collecting system information.

## Results Examples

### JSON Format

`results/results.json` - Sample output in JSON format.

### YAML Format

`results/results.yaml` - Sample output in YAML format.

## Usage

To run any of these examples:

```bash
# Using the full command
serverinspector run configs/basic_test.yaml

# Using the short command
si run configs/basic_test.yaml

# Output to a specific format
si run configs/comprehensive_test.yaml --output-format json --output-file my_results.json
```

See the main documentation for more information on how to use serverinspector.
