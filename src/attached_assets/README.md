# Attached Assets

This directory contains static assets used by ServerInspect, such as:

- Templates for report generation
- Default configuration files
- Static resources

These assets are packaged with the application and can be accessed at runtime.

## Adding New Assets

To add new assets, simply place them in this directory and they will be included in the package.

## Accessing Assets

Assets can be accessed programmatically using:

```python
import pkgutil
import attached_assets

# Load an asset
asset_data = pkgutil.get_data("attached_assets", "path/to/asset.txt")
``` 