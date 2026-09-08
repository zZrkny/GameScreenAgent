import time
from pathlib import Path

import cv2
import pyautogui

from src.capture import capture_window
from src.vision import find_template, find_all_templates
from src.agent import AgentAction


pyautogui.FAILSAFE = True

SHOP_ROI = (0.25, 0.20, 0.75, 0.53)

HAND_ROI = (0.30, 0.72, 0.70, 1.00)

HERO_2_POSITION = (0.41, 0.45)

BUY_TARGET = (0.50, 0.72)

PLAY_TARGET = (0.50, 0.55)

TRINKET_OPTION_2 = (
    0.43,
    0.39,
)

TRINKET_CONFIRM = (
    0.50,
    0.69,
)

def normalized_to_screen(region, position):
    nx, ny = position

    x = region["left"] + int(region["width"] * nx)
    y = region["top"] + int(region["height"] * ny)

    return x, y

def detect_hand_minions(
    screen_path,
    template_paths
):
    detections = find_all_templates(
        screen_path,
        template_paths,
        threshold=0.85,
        roi=HAND_ROI,
        scales=(
            0.55,
            0.60,
            0.65,
            0.70,
            0.75,
            0.80,
            0.85,
        ),
        min_distance=40
    )

    return detections

def detect_shop_minions(
    screen_path,
    template_paths
):
    return find_all_templates(
        screen_path,
        template_paths,
        threshold=0.90,
        roi=SHOP_ROI,
        scales=(1.0,),
        min_distance=50
    )

def play_rightmost_hand_minion(
    screen_path,
    region,
    template_paths
):
    hand_minions = detect_hand_minions(
        screen_path,
        template_paths
    )

    if not hand_minions:
        print("No hand minion detected.")
        return False

    # find_all_templates 已经按照 x 从左到右排序
    # 所以 [-1] 就是最右边，也就是通常最新买到的牌
    anchor_x, anchor_y, score = \
        hand_minions[-1]

    image = cv2.imread(screen_path)

    if image is None:
        return False

    height, width = image.shape[:2]

    # 星级图标位于手牌卡片左上附近
    # 向右下移动到卡牌主体
    card_local_x = (
        anchor_x
        + int(width * 0.025)
    )

    card_local_y = (
        anchor_y
        + int(height * 0.055)
    )

    start_x = (
        region["left"]
        + card_local_x
    )

    start_y = (
        region["top"]
        + card_local_y
    )

    end_x, end_y = normalized_to_screen(
        region,
        PLAY_TARGET
    )

    print(
        f"Playing hand minion "
        f"(confidence {score:.3f})"
    )

    pyautogui.moveTo(
        start_x,
        start_y,
        duration=0.2
    )

    pyautogui.dragTo(
        end_x,
        end_y,
        duration=0.6,
        button="left"
    )

    return True

def click_template(
    screen_path,
    template_path,
    region,
    threshold=0.85
):
    found, score, top_left, bottom_right = find_template(
        screen_path,
        template_path,
        threshold
    )

    if not found:
        return False

    local_x = (top_left[0] + bottom_right[0]) // 2
    local_y = (top_left[1] + bottom_right[1]) // 2

    screen_x = region["left"] + local_x
    screen_y = region["top"] + local_y

    pyautogui.click(screen_x, screen_y)

    return True

def select_hero_2(region, window_title):
    hero_x, hero_y = normalized_to_screen(
        region,
        HERO_2_POSITION
    )

    pyautogui.click(hero_x, hero_y)

    time.sleep(1)

    result = capture_window(window_title)

    if result is None:
        return False

    screen_path, _, new_region = result

    return click_template(
        screen_path,
        "assets/templates/actions/confirm_button.png",
        new_region,
        0.85
    )

def select_trinket(
    region,
    window_title
):
    for position in TRINKET_OPTIONS:
        x, y = normalized_to_screen(
            region,
            position
        )

        pyautogui.click(x, y)

        time.sleep(0.6)

        result = capture_window(
            window_title
        )

        if result is None:
            return False

        screen_path, _, new_region = result

        found, _, _, _ = find_template(
            screen_path,
            "assets/templates/actions/confirm_button.png",
            0.85
        )

        if found:
            success = click_template(
                screen_path,
                "assets/templates/actions/confirm_button.png",
                new_region,
                0.85
            )

            return success

    return False

def buy_and_play_leftmost(
    screen_path,
    region,
    window_title
):
    # =====================================
    # 1. 找到所有星级模板
    # =====================================

    template_paths = [
        str(path)
        for path in Path(
            "assets/templates/actions"
        ).glob("minion_tier_*.png")
    ]

    if not template_paths:
        print("No minion tier templates found.")
        return True

    # =====================================
    # 2. 如果上一次有随从没打出去
    #    先尝试处理现有手牌
    # =====================================

    existing_hand = detect_hand_minions(
        screen_path,
        template_paths
    )

    if existing_hand:
        print(
            f"Detected {len(existing_hand)} "
            f"existing hand minion(s). "
            f"Trying to play one first."
        )

        play_rightmost_hand_minion(
            screen_path,
            region,
            template_paths
        )

        time.sleep(0.8)

        # 打完以后重新截图
        result = capture_window(
            window_title
        )

        if result is None:
            return True

        screen_path, _, region = result

    # =====================================
    # 3. 购买前统计商店随从
    # =====================================

    shop_before = detect_shop_minions(
        screen_path,
        template_paths
    )

    if not shop_before:
        print("No shop minions detected.")
        return True

    shop_count_before = len(shop_before)

    print(
        f"Detected "
        f"{shop_count_before} "
        f"shop minions."
    )

    # 最左边随从
    anchor_x, anchor_y, score = \
        shop_before[0]

    print(
        f"Leftmost minion confidence: "
        f"{score:.3f}"
    )

    image = cv2.imread(screen_path)

    if image is None:
        return True

    height, width = image.shape[:2]

    # =====================================
    # 4. 根据星标推算随从主体中心
    # =====================================

    start_local_x = anchor_x

    start_local_y = (
        anchor_y
        + int(height * 0.10)
    )

    start_x = (
        region["left"]
        + start_local_x
    )

    start_y = (
        region["top"]
        + start_local_y
    )

    buy_x, buy_y = normalized_to_screen(
        region,
        BUY_TARGET
    )

    # 购买前的手牌数量
    hand_before = detect_hand_minions(
        screen_path,
        template_paths
    )

    hand_count_before = len(hand_before)

    # =====================================
    # 5. 执行购买
    # =====================================

    pyautogui.moveTo(
        start_x,
        start_y,
        duration=0.2
    )

    pyautogui.dragTo(
        buy_x,
        buy_y,
        duration=0.6,
        button="left"
    )

    # =====================================
    # 6. 等待并反复检查购买结果
    #
    # 不再只等 1 秒检查一次
    # 因为炉石动画可能还没有结束
    # =====================================

    purchase_confirmed = False

    latest_screen_path = screen_path
    latest_region = region

    latest_hand = hand_before

    for attempt in range(8):
        time.sleep(0.4)

        result = capture_window(
            window_title
        )

        if result is None:
            continue

        new_screen_path, _, new_region = \
            result

        shop_after = detect_shop_minions(
            new_screen_path,
            template_paths
        )

        hand_after = detect_hand_minions(
            new_screen_path,
            template_paths
        )

        latest_screen_path = \
            new_screen_path

        latest_region = \
            new_region

        latest_hand = \
            hand_after

        shop_count_after = \
            len(shop_after)

        hand_count_after = \
            len(hand_after)

        print(
            f"Purchase check "
            f"{attempt + 1}: "
            f"shop "
            f"{shop_count_before}"
            f" -> "
            f"{shop_count_after}, "
            f"hand "
            f"{hand_count_before}"
            f" -> "
            f"{hand_count_after}"
        )

        # ----------------------------
        # 两种证据任意满足一种：
        #
        # A. 商店随从减少
        # B. 手牌随从增加
        # ----------------------------

        if (
            shop_count_after
            < shop_count_before
        ):
            purchase_confirmed = True

        if (
            hand_count_after
            > hand_count_before
        ):
            purchase_confirmed = True

        # 如果已经确认购买，而且手牌也检测出来
        # 就可以直接结束等待
        if (
            purchase_confirmed
            and hand_count_after
            > hand_count_before
        ):
            break

    # =====================================
    # 7. 如果商店完全没变化
    #
    # 可能是：
    # - 没金币
    # - 拖拽失败
    # - 当前无法购买
    #
    # v0.2 不无限重试
    # =====================================

    if not purchase_confirmed:
        print(
            "Purchase not confirmed. "
            "Stopping actions for this "
            "shop phase."
        )

        # 注意这里必须 True
        #
        # True = 本轮动作已经处理完
        # 不要在同一个 SHOP_PHASE 无限重复
        return True

    print("Purchase confirmed.")

    # =====================================
    # 8. 购买成功以后等手牌真正出现
    # =====================================

    if (
        len(latest_hand)
        <= hand_count_before
    ):
        print(
            "Purchase confirmed by shop count, "
            "but hand card is not visible yet."
        )

        # 再额外等一小会
        for _ in range(6):
            time.sleep(0.4)

            result = capture_window(
                window_title
            )

            if result is None:
                continue

            latest_screen_path, _, \
                latest_region = result

            latest_hand = \
                detect_hand_minions(
                    latest_screen_path,
                    template_paths
                )

            if (
                len(latest_hand)
                > hand_count_before
            ):
                break

    # =====================================
    # 9. 手里已经出现随从
    #    把最新一张拖上场
    # =====================================

    if (
        len(latest_hand)
        > hand_count_before
    ):
        print(
            f"Hand minions: "
            f"{hand_count_before}"
            f" -> "
            f"{len(latest_hand)}"
        )

        play_rightmost_hand_minion(
            latest_screen_path,
            latest_region,
            template_paths
        )

        time.sleep(0.6)

    else:
        print(
            "Could not detect the purchased "
            "minion in hand."
        )

    # 无论手牌识别是否成功，
    # 都不要在当前 SHOP_PHASE 再购买一次
    return True

def execute_action(
    action,
    screen_path,
    region,
    window_title
):
    if action == AgentAction.START_GAME:
        return click_template(
            screen_path,
            "assets/templates/states/battlegrounds_start.png",
            region
        )

    if action == AgentAction.SELECT_HERO_2:
        return select_hero_2(
            region,
            window_title
        )

    if action == AgentAction.SELECT_TRINKET:
        return select_trinket(
            region,
            window_title
        )

    if action == AgentAction.BUY_AND_PLAY_LEFTMOST:
        return buy_and_play_leftmost(
            screen_path,
            region,
            window_title
        )

    if action == AgentAction.RETURN_TO_MENU:
        x, y = normalized_to_screen(
            region,
            (0.50, 0.50)
        )

        pyautogui.click(
            x,
            y
        )

        return True

    # WAIT
    return True

def select_trinket(
    region,
    window_title
):
    # 1. 固定选择第二个饰品
    option_x, option_y = normalized_to_screen(
        region,
        TRINKET_OPTION_2
    )

    print("Selecting trinket option 2.")

    pyautogui.click(
        option_x,
        option_y
    )

    # 给游戏一点时间更新 UI
    time.sleep(0.8)

    # 2. 固定点击下方确认按钮
    confirm_x, confirm_y = normalized_to_screen(
        region,
        TRINKET_CONFIRM
    )

    print("Confirming trinket selection.")

    pyautogui.click(
        confirm_x,
        confirm_y
    )

    # 等弹窗关闭
    time.sleep(1.0)

    return True