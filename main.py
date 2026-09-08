from src.capture import capture_window
from src.vision import find_template, draw_match


result = capture_window("炉石")

if result is None:
    print("Game window not found.")

else:
    screen_path, title = result

    print(f"Window found: {title}")
    print(f"Screenshot saved to: {screen_path}")

    found, score, top_left, bottom_right = find_template(
        screen_path,
        "assets/templates/target.png"
    )

    print()
    print("Template: target.png")
    print(f"Found: {found}")
    print(f"Confidence: {score:.3f}")

    if found:
        debug_path = draw_match(
            screen_path,
            top_left,
            bottom_right
        )

        print(f"Debug image saved to: {debug_path}")