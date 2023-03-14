import pyrealsense2 as rs

# Create a context object
ctx = rs.context()

# Get the available devices
devices = ctx.query_devices()

# Print the device information
for dev in devices:
    print(f"Device name: {dev.get_info(rs.camera_info.name)}")
    print(f"Serial number: {dev.get_info(rs.camera_info.serial_number)}")
    print(f"Firmware version: {dev.get_info(rs.camera_info.firmware_version)}")
    print("Supported configurations:")
    for sensor in dev.sensors:
        for profile in sensor.get_stream_profiles():
            print(f"\t{profile.stream_name()} ({profile.stream_type()}) - {profile.fps} fps")
