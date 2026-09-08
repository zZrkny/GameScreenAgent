import cv2


def find_template(screen_path, template_path, threshold=0.85):
    screen = cv2.imread(screen_path)
    template = cv2.imread(template_path)

    if screen is None:
        raise FileNotFoundError(f"Could not load screen image: {screen_path}")

    if template is None:
        raise FileNotFoundError(f"Could not load template image: {template_path}")

    screen_gray = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)
    template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

    template_height, template_width = template_gray.shape

    result = cv2.matchTemplate(
        screen_gray,
        template_gray,
        cv2.TM_CCOEFF_NORMED
    )

    _, max_score, _, max_location = cv2.minMaxLoc(result)

    found = max_score >= threshold

    top_left = max_location
    bottom_right = (
        top_left[0] + template_width,
        top_left[1] + template_height
    )

    return found, max_score, top_left, bottom_right

def draw_match(
    screen_path,
    top_left,
    bottom_right,
    output_path="debug_match.png"
):
    image = cv2.imread(screen_path)

    if image is None:
        raise FileNotFoundError(f"Could not load image: {screen_path}")

    cv2.rectangle(
        image,
        top_left,
        bottom_right,
        (0, 255, 0),
        3
    )

    cv2.imwrite(output_path, image)

    return output_path