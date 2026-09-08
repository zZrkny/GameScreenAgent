from src.states import GameState
from src.vision import find_template


STATE_TEMPLATES = {
    GameState.WEEKLY_QUEST_POPUP: (
        "assets/templates/states/weekly_quest.png",
        0.85
    ),
    
    GameState.TRINKET_SELECT: (
        "assets/templates/states/trinket_select.png",
        0.85
    ),

    GameState.HERO_SELECT: (
        "assets/templates/states/hero_select.png",
        0.85
    ),

    GameState.RESULT: (
        "assets/templates/states/result.png",
        0.85
    ),

    GameState.BATTLEGROUNDS_MENU: (
        "assets/templates/states/battlegrounds_start.png",
        0.85
    ),

    GameState.SHOP_PHASE: (
        "assets/templates/states/shop_phase.png",
        0.85
    ),
}


STATE_PRIORITY = [
    GameState.WEEKLY_QUEST_POPUP,
    GameState.TRINKET_SELECT,
    GameState.HERO_SELECT,
    GameState.RESULT,
    GameState.BATTLEGROUNDS_MENU,
    GameState.SHOP_PHASE,
]


def detect_state(screen_path):
    for state in STATE_PRIORITY:
        template_path, threshold = \
            STATE_TEMPLATES[state]

        found, score, _, _ = find_template(
            screen_path,
            template_path,
            threshold
        )

        if found:
            return state, score

    return GameState.UNKNOWN, 0.0