import mss
import mss.tools


def capture_screen(output_path="screenshot.png"):
    with mss.mss() as sct:
        monitor = sct.monitors[1]
        screenshot = sct.grab(monitor)

        mss.tools.to_png(
            screenshot.rgb,
            screenshot.size,
            output=output_path
        )

    return output_path