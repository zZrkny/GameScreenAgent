import time

from src.capture import capture_window
from src.state_detector import detect_state
from src.agent import decide
from src.actions import execute_action


GAME_WINDOW_TITLE = "炉石"

POLL_INTERVAL = 1.0
STABLE_FRAMES = 2


last_candidate = None
candidate_count = 0

stable_state = None
action_done = False


print("GameScreenAgent v0.1 started.")
print("Press Ctrl+C to stop.")


try:

    while True:

        result = capture_window(
            GAME_WINDOW_TITLE
        )

        if result is None:
            print("Game window not found.")
            time.sleep(POLL_INTERVAL)
            continue

        screen_path, title, region = result

        state, score = detect_state(
            screen_path
        )

        # 防止识别偶尔闪一下
        if state == last_candidate:
            candidate_count += 1
        else:
            last_candidate = state
            candidate_count = 1

        if candidate_count >= STABLE_FRAMES:

            if state != stable_state:

                stable_state = state
                action_done = False

                print()
                print(
                    f"State: {state.value} "
                    f"({score:.3f})"
                )

            if not action_done:

                action = decide(state)

                print(
                    f"Decision: {action.value}"
                )

                success = execute_action(
                    action,
                    screen_path,
                    region,
                    GAME_WINDOW_TITLE
                )

                if success:
                    action_done = True

        time.sleep(POLL_INTERVAL)


except KeyboardInterrupt:

    print()
    print("GameScreenAgent stopped.")