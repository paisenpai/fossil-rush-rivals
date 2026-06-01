# 🦕 Fossil Rush Rivals

> A turn-based strategy game where you race an adaptive AI to excavate, authenticate, and auction the most valuable fossils from an active dig site.

**COSC 304 – Introduction to Artificial Intelligence** · A.Y. 2025–2026  
Polytechnic University of the Philippines · BSCS 3-2

---

## Table of Contents

- [Overview](#overview)
- [Gameplay](#gameplay)
- [AI System](#ai-system)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
- [Team](#team)

---

## Overview

Fossil Rush Rivals is a 2D pixel-art strategy game built in Python/Pygame. Unlike games with scripted AI opponents, this project features a **multi-algorithm AI pipeline** that reads the board in real time and combines outputs from four distinct machine learning models into a single, adaptive decision engine.

This makes the AI genuinely challenging - it doesn't follow a fixed script, it responds to *your* strategy.

---

## Gameplay

Each round follows a full **day–night cycle** divided into three phases:

### ☀️ Phase 1 - Excavation (Day)
Players alternate turns digging tiles on a 2D map, spending from a limited budget each turn. A tile may reveal a bone fragment, a complete fossil, or a worthless decoy rock.

### 🔬 Phase 2 - Lab Verification (Night)
Excavated finds are analyzed and assigned one of four authenticity ratings - **Verified**, **Uncertain**, **Suspicious**, or **Fake** - which directly determines their market value heading into the auction.

### 🌙 Phase 3 - Midnight Market (Midnight)
An AI-driven panel of buyers evaluates both collections at auction. The player with the highest total valuation wins the round.

---

## AI System

The AI opponent runs a **parallel evaluation pipeline**: when choosing an action, four specialized models each score every candidate tile from `0.00` to `1.00`. Their scores are combined into a single weighted decision.

| # | Model | Algorithm | Confidence | Role |
|---|-------|-----------|------------|------|
| 1 | **Map** | K-Means Clustering | 0.85 | Identifies high-yield dig zones from past fossil locations |
| 2 | **Radar** | Expectation-Maximization | 0.82 | Predicts the shape and direction of partially-uncovered skeletons |
| 3 | **Manual** | Decision Tree | 0.60 | Enforces rule-based logic and prevents illegal or wasteful moves |
| 4 | **Gut** | Neural Network (Backprop) | 0.96 | Balances continuous trade-offs with fluid, human-like intuition |

### How Each Model Contributes

**Map (K-Means)** groups historical fossil coordinates into hotspot zones, acting as a geographic compass. This prevents the AI from wandering into barren sectors.

**Radar (EM)** goes beyond simple circles - it learns the orientation of elongated deposits, so once a single bone is found, it predicts which direction the rest of the skeleton stretches. This makes skeleton-following efficient and accurate.

**Manual (Decision Tree)** is the logical backbone. It asks hard yes/no questions about game rules and action order, keeping the AI from making structural errors that the smoother models might miss.

**Gut (Neural Network)** processes all board variables simultaneously and weighs competing priorities - rival proximity, dig budget, skeleton value, time remaining - to produce flexible decisions that adapt to complex mid-game situations.

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| Language | Python |
| Game Engine | Pygame (2D retro pixel-art rendering) |
| Clustering / Trees | K-Means, Decision Tree, EM, AdaBoost |
| Neural Network | NumPy / PyTorch (Backpropagation) |

---

## Getting Started

### Prerequisites
- Python 3.9+
- `pip` and `venv`

### 1. Clone the Repository

```bash
git clone https://github.com/paisenpai/fossil-rush-rivals.git
cd fossil-rush-rivals
```

### 2. Create and Activate a Virtual Environment

```bash
# Create
python -m venv .venv

# Activate - Windows (PowerShell)
.\.venv\Scripts\Activate.ps1

# Activate - macOS / Linux
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Train the AI Models *(optional but recommended)*

Generates synthetic training data and trains all five models from scratch. Skip this step to use the pre-trained weights included in the repo.

```bash
python ai_training/generate_synthetic_data.py
python ai_training/train_kmeans.py
python ai_training/train_decision_tree.py
python ai_training/train_em_model.py
python ai_training/train_adaboost.py
python ai_training/train_market_nn.py
python ai_training/export_models.py
```

### 5. Run the Game

```bash
python -m fossil_rush_rivals.game.main
```

---

## Team

| Name | Role |
|------|------|
| Deposoy, John Gavin | |
| Lagman, John Ferry D. | |
| Reyes, Redd Lawrence M. | |
| Sagun, Eujin Rod L. | |
