# Pixel Pawn

A retro-styled, isometric, hand-drawn pixel art chess game built in Python with Pygame.

This project blends classic chess gameplay with a warm, nostalgic arcade aesthetic inspired by old-school pixel games. The board is presented in an isometric layout, pieces are drawn in a hand-crafted style, and the experience includes a timer, move take-back, and a simple AI opponent.

## Features

- Isometric chess board with a hand-drawn pixel art look
- Chess timer for both sides
- Move take-back support
- AI difficulty settings
- Retro UI with custom graphics and a low-fi, arcade feel
- Playable prototype built for local desktop play

## Gameplay

- Select a piece by clicking it
- Drag and drop to move it
- Use the in-game menu for draw/home actions
- Watch the timer and manage your turns carefully
- Try the AI modes and experiment with different difficulties

## Controls

- Left click: select and move pieces
- Mouse drag: reposition a selected piece
- In-game menu: pause, offer a draw, or return home

## Running the game

Requirements:

- Python 3
- Pygame

Install dependencies:

```bash
pip install pygame
```

Run the game:

```bash
python main.py
```

## Project notes

This project is still in active development. The gameplay loop, UI, and AI are being iterated on, and the setup screen/demo flow is not fully finished yet.

The repo also includes browser/demo packaging assets, but the main project is still centered around the Pygame prototype in `main.py`.

## Project structure

```text
.
├── main.py                 # Main game logic and rendering
├── index.html              # Browser/demo bootstrap
├── graphics/               # Sprites, board art, UI assets
├── fonts/                  # Pixel fonts
├── build/                  # Build-related files
├── favicon.png             # App icon
├── README.md               # Project overview
└── pixel-pawn-demoitch/    # Demo packaging assets
```

## A note from the creator

"ps don't click setup yet, i'm still working on it"

This project is a work in progress, but the goal is to make a fun, retro-feeling chess experience with lots of personality.

Thanks for checking it out — hope you have fun.
