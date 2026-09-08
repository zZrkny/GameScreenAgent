from enum import Enum
from src.states import GameState


class AgentAction(Enum):
    WAIT = "WAIT"
    START_GAME = "START_GAME"
    SELECT_HERO_2 = "SELECT_HERO_2"
    SELECT_TRINKET = "SELECT_TRINKET"
    BUY_AND_PLAY_LEFTMOST = "BUY_AND_PLAY_LEFTMOST"
    RETURN_TO_MENU = "RETURN_TO_MENU"
    DISMISS_WEEKLY_QUEST = "DISMISS_WEEKLY_QUEST"


def decide(state):
    if state == GameState.BATTLEGROUNDS_MENU:
        return AgentAction.START_GAME

    if state == GameState.HERO_SELECT:
        return AgentAction.SELECT_HERO_2

    if state == GameState.TRINKET_SELECT:
        return AgentAction.SELECT_TRINKET

    if state == GameState.SHOP_PHASE:
        return AgentAction.BUY_AND_PLAY_LEFTMOST

    if state == GameState.RESULT:
        return AgentAction.RETURN_TO_MENU
    
    if state == GameState.WEEKLY_QUEST_POPUP:
        return AgentAction.DISMISS_WEEKLY_QUEST

    return AgentAction.WAIT