# GameScreenAgent

A Python desktop automation project exploring screen perception, state detection, decision-making, and UI interaction.

## Current Status

**Version: v0.2**

GameScreenAgent can now complete a full automated state-based loop using computer vision and rule-based decisions.

The project was built step by step as a learning project for Python, computer vision, desktop automation, state machines, and agent architecture.

## Architecture

Screen
  ↓
Capture
  ↓
Perception
  ↓
State
  ↓
Decision
  ↓
Action
  ↓
Screen


The current agent is rule-based and does not use an LLM or machine-learning model.

Features：
  Detect the target game window
  Capture the game screen
  OpenCV template matching
  Multi-scale template matching
  Region of Interest (ROI) detection
  Game-state detection
  Rule-based decisions
  Mouse clicking and dragging
  Action verification
  Continuous Observe → Decide → Act loop
  
  Current detectable states include:
    Battlegrounds menu
    Hero selection
    Trinket selection
    Shop phase
    Result screen
    Weekly quest popup
    Unknown / passive states
  
  Current automated actions include:
    Start a match
    Select and confirm a hero
    Select and confirm a trinket
    Detect shop minions
    Buy the leftmost minion
    Play a purchased minion from hand
    Wait through passive / combat states
    Dismiss result and quest screens
    Continue into the next match

Project_Structure:
  GameScreenAgent/
  ├── assets/
  │   └── templates/
  │       ├── states/
  │       └── actions/
  ├── src/
  │   ├── capture.py
  │   ├── vision.py
  │   ├── states.py
  │   ├── state_detector.py
  │   ├── agent.py
  │   └── actions.py
  ├── .gitignore
  ├── main.py
  ├── README.md
  └── requirements.txt

Setup:
  python -m venv .venv
  .\.venv\Scripts\Activate.ps1
  python -m pip install -r requirements.txt
  python main.py
