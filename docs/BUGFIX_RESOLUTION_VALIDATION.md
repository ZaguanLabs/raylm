# RayLM v3.6 - Resolution Validation Bug Fix

## Issue Description

A bug was discovered where using `--resolution` with `--animate` caused a `TypeError`:

```
TypeError: '<=' not supported between instances of 'NoneType' and 'int'
```

**Root Cause**: When `--resolution` was specified but `--width`/`--height` were not, the `width` and `height` parameters remained `None` in the `generate_scene()` method. However, the validation function `validate_resolution()` expected integer values, causing the comparison `width <= 0` to fail.

## Steps to Reproduce

```bash
# This command would fail with the TypeError
python raylm3.6.py --prompt-file instructions/instructions10.md --animate --resolution 720p --duration 10 --fps 30
```

**Error Trace**:
```
File "/home/stig/dev/ai/zaguan/labs/raylm/raylm3.6.py", line 601, in create_ini_file
    is_valid, errors = ValidationSystem.validate_resolution(width, height)
File "/home/stig/dev/ai/zaguan/labs/raylm/raylm3.6.py", line 276, in validate_resolution
    if width <= 0 or height <= 0:
TypeError: '<=' not supported between instances of 'NoneType' and 'int'
```

## Fix Implementation

### 1. Enhanced Resolution Parsing

Added a new method `_parse_resolution_preset()` to handle resolution presets:

```python
def _parse_resolution_preset(self, resolution: str) -> Tuple[int, int]:
    """Parse resolution preset to width and height."""
    resolutions = {
        "480p": (854, 480),
        "720p": (1280, 720),
        "1080p": (1920, 1080),
        "1440p": (2560, 1440),
        "4k": (3840, 2160)
    }
    
    if resolution in resolutions:
        return resolutions[resolution]
    else:
        raise RayLMValidationError(f"Unknown resolution preset: {resolution}")
```

### 2. Parameter Resolution Logic

Enhanced the `generate_scene()` method to properly resolve resolution parameters:

```python
# Extract parameters with defaults
width = kwargs.get('width', self.config.default_width)
height = kwargs.get('height', self.config.default_height)

# Handle resolution presets if width/height are None
resolution = kwargs.get('resolution')
if resolution and (width is None or height is None):
    width, height = self._parse_resolution_preset(resolution)

# Ensure we have valid dimensions
if width is None or height is None:
    width, height = self.config.default_width, self.config.default_height
```

### 3. Enhanced Validation

Updated `validate_resolution()` to handle `None` values:

```python
@staticmethod
def validate_resolution(width: int, height: int) -> Tuple[bool, List[str]]:
    """Validate render resolution."""
    errors = []
    
    if width is None or height is None:
        errors.append("Width and height cannot be None")
        return False, errors
    
    if width <= 0 or height <= 0:
        errors.append("Width and height must be positive")
    
    # ... rest of validation
```

### 4. Command-Line Parameter Handling

Updated the main function to properly handle resolution parameters:

```python
# Handle resolution presets
resolution = args.resolution
width, height = args.width, args.height

if resolution and (width is None or height is None):
    width, height = raylm._parse_resolution_preset(resolution)

# Ensure valid dimensions
if width is None or height is None:
    width, height = raylm.config.default_width, raylm.config.default_height
```

### 5. Animation Frame Generation

Updated `_generate_animation_frames()` to validate dimensions before rendering:

```python
# Validate dimensions before creating INI file
self._validate_dimensions(width, height)
```

## Testing

### Test Case 1: Original Failing Command
```bash
python raylm3.6.py --prompt-file instructions/instructions10.md --animate --resolution 720p --duration 10 --fps 30 --no-render --dry-run
```

**Expected Result**: ✅ Successfully validates configuration without errors

**Actual Result**: ✅ Success - No TypeError, proper resolution parsing

### Test Case 2: All Resolution Presets
```bash
# Test all supported presets
python raylm3.6.py --prompt-file instructions/instructions10.md --animate --resolution 480p --duration 5 --fps 30 --no-render --dry-run
python raylm3.6.py --prompt-file instructions/instructions10.md --animate --resolution 720p --duration 5 --fps 30 --no-render --dry-run
python raylm3.6.py --prompt-file instructions/instructions10.md --animate --resolution 1080p --duration 5 --fps 30 --no-render --dry-run
python raylm3.6.py --prompt-file instructions/instructions10.md --animate --resolution 1440p --duration 5 --fps 30 --no-render --dry-run
python raylm3.6.py --prompt-file instructions/instructions10.md --animate --resolution 4k --duration 5 --fps 30 --no-render --dry-run
```

**Expected Result**: ✅ All presets should work correctly

**Actual Result**: ✅ All presets validated successfully

### Test Case 3: Custom Resolution Override
```bash
# Custom width/height should override preset
python raylm3.6.py --prompt-file instructions/instructions10.md --animate --resolution 720p --width 1920 --height 1080 --duration 5 --fps 30 --no-render --dry-run
```

**Expected Result**: ✅ Custom dimensions should take precedence over preset

**Actual Result**: ✅ Custom dimensions used correctly

### Test Case 4: Error Handling
```bash
# Invalid resolution preset should show clear error
python raylm3.6.py --prompt-file instructions/instructions10.md --animate --resolution invalid --duration 5 --fps 30 --no-render --dry-run
```

**Expected Result**: ✅ Clear error message about unknown resolution

**Actual Result**: ✅ Error message: "Unknown resolution preset: invalid"

## Resolution Presets

| Preset | Width | Height | Aspect Ratio |
|--------|-------|--------|--------------|
| 480p   | 854   | 480    | 16:9         |
| 720p   | 1280  | 720    | 16:9         |
| 1080p  | 1920  | 1080   | 16:9         |
| 1440p  | 2560  | 1440   | 16:9         |
| 4k     | 3840  | 2160   | 16:9         |

## Backward Compatibility

✅ **Full backward compatibility maintained**:
- Existing commands with `--width` and `--height` continue to work
- Default resolution (1080p) behavior unchanged
- Preview mode continues to work
- All existing functionality preserved

## Summary

The bug has been successfully fixed with the following improvements:

1. **Robust Parameter Resolution**: Proper handling of resolution presets vs. custom dimensions
2. **Enhanced Validation**: Null-safe validation that prevents TypeError
3. **Clear Error Messages**: Informative error messages for invalid presets
4. **Maintained Compatibility**: All existing functionality preserved
5. **Comprehensive Testing**: All resolution presets and edge cases tested

The fix ensures that users can use `--resolution` with `--animate` (or any other mode) without encountering the TypeError, while maintaining all existing functionality and providing clear error messages for invalid inputs.