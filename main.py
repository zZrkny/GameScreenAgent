from src.capture import capture_window


result = capture_window("炉石")

if result is None:
    print("Game window not found.")
else:
    output_path, title = result

    print(f"Window found: {title}")
    print(f"Screenshot saved to: {output_path}")