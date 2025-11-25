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

📄 License

 GNU GENERAL PUBLIC LICENSE
                       Version 3, 29 June 2007

 Copyright (C) 2007 Free Software Foundation, Inc. <https://fsf.org/>
 Everyone is permitted to copy and distribute verbatim copies
 of this license document, but changing it is not allowed.

👤 Author

Daniel Cannon (codejacket.io)

Portfolio: https://codejacket.io