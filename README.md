# ♠️ Solitaire – Python Game (Pygame)

A fully interactive **Solitaire (Klondike)** card game built in **Python** using **Pygame**.  
This project demonstrates object-oriented game architecture, sprite rendering, animations, state management, and custom art assets. It runs locally on macOS, Windows, and Linux.

<p align="center">
  <img src="assets/demoScreenShot.png" width="600"/>
</p>

---

## ✨ Features

- 🃏 **Classic Klondike rules**
- ⬆️ **Drag-and-drop card movement**
- 🔄 **Animated card flipping**
- ⭐ **Custom card artwork** (PNG)
- 🔢 **Auto-stacking logic** for foundations
- 🗃️ **Game state management**
- 🎨 **Smooth rendering using Pygame**
- ⌨️ Keyboard shortcuts:
  - `N` → New game  
  - `U` → Undo (if implemented)  
  - `Esc` → Quit  

---

## 🧱 Project Structure

solitaire/
├── assets/
│ ├── cards/ # 52 card PNGs + back.png
│ ├── ui/ # optional buttons, icons
│ └── screenshot.png
│
├── src/
│ ├── card.py # Card class (rank, suit, face-up, image)
│ ├── deck.py # Generates and shuffles deck
│ ├── pile.py # Tableau, foundation, waste, stock
│ ├── game.py # Core Solitaire rules + state transitions
│ ├── ui.py # Rendering, animations, hitboxes
│ └── main.py # Game loop entry point
│
├── requirements.txt
└── README.md


---

## 🚀 Installation

### **1. Clone the repository**
```bash
git clone https://github.com/<diydaniel>/Solitaire-Python.git
cd Solitaire-Python

# 2. Create a virtual environment
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
# OR
.venv\Scripts\activate     # Windows

# 3. Install dependencies
pip install -r requirements.txt

▶️ Running the Game
    From the project root:

    python src/main.py

🧠 How It Works (Technical Walkthrough)
    Game Loop

    Runs at FPS = 60:

    Handles events (mouse, keyboard)

    Updates card states (dragging, flipping)

    Renders screen

    Card Rendering

    Each card is a pygame.Surface loaded from assets/cards/??.png.

    Cards are layered with:

    z-index

    Current pile index

    Whether it is being dragged

    Rules Engine

    game.py enforces:

    Valid moves between tableaus

    Only kings may move to empty rows

    Foundations must build ascending by suit

    Flipping rules for waste/stock

    Animations

    Designed using:

    Incremental frame-based movement

    Smooth transitions for flips and slides