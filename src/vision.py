import cv2
import numpy as np


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

def find_all_templates(
    screen_path,
    template_paths,
    threshold=0.90,
    roi=None,
    min_distance=50,
    scales=(1.0,)
):
    screen = cv2.imread(screen_path)

    if screen is None:
        raise FileNotFoundError(
            f"Could not load screen image: {screen_path}"
        )

    screen_height, screen_width = screen.shape[:2]

    # 默认搜索整张图片
    search_image = screen

    # ROI 在原图中的偏移量
    offset_x = 0
    offset_y = 0

    # 如果提供了 ROI，只搜索指定区域
    if roi is not None:
        left, top, right, bottom = roi

        x1 = int(screen_width * left)
        y1 = int(screen_height * top)
        x2 = int(screen_width * right)
        y2 = int(screen_height * bottom)

        search_image = screen[y1:y2, x1:x2]

        offset_x = x1
        offset_y = y1

    detections = []

    # 依次检查所有模板
    for template_path in template_paths:
        template = cv2.imread(template_path)

        if template is None:
            print(f"Warning: could not load template: {template_path}")
            continue

        # 同一个模板尝试不同大小
        for scale in scales:
            if scale <= 0:
                continue

            interpolation = (
                cv2.INTER_AREA
                if scale < 1.0
                else cv2.INTER_LINEAR
            )

            resized_template = cv2.resize(
                template,
                None,
                fx=scale,
                fy=scale,
                interpolation=interpolation
            )

            template_height, template_width = \
                resized_template.shape[:2]

            search_height, search_width = \
                search_image.shape[:2]

            # 模板比搜索区域还大时无法匹配
            if (
                template_width > search_width
                or template_height > search_height
            ):
                continue

            result = cv2.matchTemplate(
                search_image,
                resized_template,
                cv2.TM_CCOEFF_NORMED
            )

            ys, xs = np.where(
                result >= threshold
            )

            for x, y in zip(xs, ys):
                center_x = (
                    offset_x
                    + x
                    + template_width // 2
                )

                center_y = (
                    offset_y
                    + y
                    + template_height // 2
                )

                score = float(result[y, x])

                detections.append(
                    (
                        center_x,
                        center_y,
                        score
                    )
                )

    # -----------------------------
    # 去掉同一个目标产生的重复匹配
    # -----------------------------

    # 先让高置信度排前面
    detections.sort(
        key=lambda item: item[2],
        reverse=True
    )

    unique_detections = []

    for detection in detections:
        x, y, score = detection

        too_close = False

        for existing in unique_detections:
            existing_x, existing_y, _ = existing

            distance_squared = (
                (x - existing_x) ** 2
                + (y - existing_y) ** 2
            )

            if distance_squared < min_distance ** 2:
                too_close = True
                break

        if not too_close:
            unique_detections.append(
                detection
            )

    # 最终按照屏幕上的 x 坐标从左到右排序
    unique_detections.sort(
        key=lambda item: item[0]
    )

    return unique_detections