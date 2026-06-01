```markdown
# Fossil Rush Rivals

Hey! [cite_start]Welcome to **Fossil Rush Rivals**, a turn-based strategy game set in an active paleontological dig site[cite: 24, 78]. [cite_start]You play as a paleontologist competing against a super smart, highly adaptive AI rival to excavate, verify, and sell the highest value fossils[cite: 24, 25, 36].

[cite_start]This project is a technical demonstration for **COSC 304 - Introduction to Artificial Intelligence** (A.Y. 2025-2026) at the Polytechnic University of the Philippines[cite: 10, 16, 334].

---

## 🎮 Game Concept and Phases

[cite_start]Unlike traditional board games with predictable, scripted AI, this game features a multi-algorithm AI pipeline that changes its strategy based on your moves[cite: 34, 36, 49]. [cite_start]Each round follows a full day-night cycle divided into three main phases[cite: 26, 87]:

1. [cite_start]**Excavation Phase (Day):** Players take alternating turns digging up a 2D tile map using a limited budget[cite: 26, 29, 88, 93]. [cite_start]You can find bone fragments, full fossils, or completely worthless decoy rocks[cite: 91].
2. [cite_start]**Laboratory Verification Phase (Night):** You analyze and authenticate your finds[cite: 27, 94, 358]. [cite_start]The lab determines if a fossil is Verified, Uncertain, Suspicious, or Fake, which directly dictates its market value[cite: 94, 207, 359].
3. [cite_start]**Midnight Market (Midnight):** An auctioneer and an AI-driven panel of buyers evaluate the collections[cite: 28, 98]. [cite_start]Round scores are determined by whoever gets the highest total valuation[cite: 28, 99].

---

## 🧠 System Architecture and AI Pipeline

[cite_start]The core engine routes real-time board data into specialized AI models simultaneously[cite: 49, 155, 158]. [cite_start]Their individual outputs are combined into a final evaluation score to dictate the absolute best movement or digging action[cite: 56, 159, 183].

### The Evaluation Pipeline

[cite_start]When evaluating a target tile, the models process the current board facts in parallel and output their respective confidence scores from `0.00` to `1.00`[cite: 158]:

* **1. Map (K-Means Clustering) → Confidence: 0.85**
  * [cite_start]**What it does:** Remembers the exact coordinates where fossils were successfully dug up in the past and groups them into central hotspot zones[cite: 50, 146, 165].
  * [cite_start]**How the AI uses it:** It acts as a geographical compass that directs the AI to travel, survey, and dig only near these high-yield zones[cite: 50, 165, 178].
  * [cite_start]**Why we need it:** It prevents the AI from wandering around randomly or wasting turns in empty, barren sectors of the map where fossils never spawn[cite: 36, 50].

* **2. Radar (Expectation-Maximization) → Confidence: 0.82**
  * [cite_start]**What it does:** Unlike K-Means which only sees generic circles, EM learns the exact shape and orientation (like stretched ovals) of fossil deposits in the soil[cite: 52].
  * [cite_start]**How the AI uses it:** Once a single trace like a skull or ribcage is found, EM predicts the exact direction the rest of the body is stretching in[cite: 52, 167, 180].
  * [cite_start]**Why we need it:** It acts as a soft radar, telling the AI exactly which neighboring tiles are highly likely to contain the rest of the skeleton and which are dead ends[cite: 52, 167].

* **3. Manual (Decision Tree) → Confidence: 0.60**
  * [cite_start]**What it does:** Acts like a strict field flowchart that asks yes/no questions to decide the best move[cite: 34, 51, 166].
  * [cite_start]**How the AI uses it:** It strictly controls the action order, ensuring the AI respects rules of engagement instead of doing random or blind actions[cite: 51, 166, 179].
  * [cite_start]**Why we need it:** It is the logical backbone of the AI[cite: 49, 56]. [cite_start]Other models try to smooth decisions out, but the Decision Tree keeps actions black-and-white, completely avoiding structural mistakes[cite: 51, 166].

* **4. Gut (Neural Network / Back-Propagation) → Confidence: 0.96**
  * [cite_start]**What it does:** Processes and weighs all board facts simultaneously in parallel, rather than following a rigid, one-question-at-a-time flowchart[cite: 54, 170].
  * [cite_start]**How the AI uses it:** Smoothly blends continuous variables such as balancing matching time, rival proximity, and skeleton value to make flexible, human-like decisions[cite: 54, 170, 182].
  * [cite_start]**Why we need it:** It prevents the AI from failing at rigid, blocky flowchart cutoffs, giving it the fluid tactical intuition to handle complex trade-offs[cite: 54, 171].

---

## 🛠️ Tech Stack

* [cite_start]**Language:** Python [cite: 245]
* [cite_start]**Framework:** Pygame (for the 2D retro pixel-art rendering and UI) [cite: 245, 248]
* [cite_start]**ML Libraries:** Scikit-learn (K-Means, Decision Tree, EM, AdaBoost), NumPy / PyTorch (Back-Propagation) [cite: 246, 247]

---

## 🚀 How to Set It Up

[cite_start]Follow these quick steps to clone the repo, install dependencies, and run the game[cite: 59]:

### 1. Clone the Repository
```bash
git clone [https://github.com/paisenpai/fossil-rush-rivals.git](https://github.com/paisenpai/fossil-rush-rivals.git)
cd fossil-rush-rivals

```

### 2. Create and Activate a Virtual Environment

```bash
# Create venv
python -m venv .venv

# Activate venv (Windows PowerShell)
.\.venv\Scripts\Activate.ps1

# Activate venv (Mac/Linux)
source .venv/bin/activate

```

### 3. Install Dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt

```

### 4. Train the AI Models (Optional but Recommended)

If you want to train or refresh the models using synthetic data before playing, run the training pipeline:

```bash
python ai_training\generate_synthetic_data.py
python ai_training\train_kmeans.py
python ai_training\train_decision_tree.py
python ai_training\train_em_model.py
python ai_training\train_adaboost.py
python ai_training\train_market_nn.py
python ai_training\export_models.py

```

### 5. Run the Game

```bash
python -m fossil_rush_rivals.game.main

```

---

## 👥 Proponents (BSCS 3-2)
* Deposoy, John Gavin 
* Lagman, John Ferry D. 
* Reyes, Redd Lawrence M. 
* Sagun, Eujin Rod L. 



```

```
