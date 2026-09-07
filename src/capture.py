import mss
import mss.tools
import win32gui


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

def find_window(title_keyword):
    matches = []

    def enum_callback(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)

            if title_keyword.lower() in title.lower():
                matches.append((hwnd, title))

    win32gui.EnumWindows(enum_callback, None)

    if not matches:
        return None

    return matches[0]

def get_window_region(hwnd):
    left, top, right, bottom = win32gui.GetWindowRect(hwnd)

    return {
        "left": left,
        "top": top,
        "width": right - left,
        "height": bottom - top,
    }

def capture_window(title_keyword, output_path="game_window.png"):
    window = find_window(title_keyword)

    if window is None:
        return None

    hwnd, title = window
    region = get_window_region(hwnd)

    with mss.mss() as sct:
        screenshot = sct.grab(region)

        mss.tools.to_png(
            screenshot.rgb,
            screenshot.size,
            output=output_path
        )

    return output_path, title