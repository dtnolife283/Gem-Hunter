# 💎 Gem Hunter: CNF-Based Puzzle Solver

A course project for **Artificial Intelligence (Project 2)** — 2024.  
This project focuses on solving a strategic puzzle game called **Gem Hunter** using propositional logic, CNF clause generation, and SAT solvers.

## 📜 Game Description

**Gem Hunter** is a grid-based logic game where players must uncover all hidden gems while avoiding traps. Each tile on the grid may:
- Show a **number**, indicating how many traps are adjacent.
- Be a **trap** (`T`)
- Be a **gem** (`G`)
- Or be an **empty cell** (`_`)

The goal: **Reveal all gems without triggering any traps.**

## 🧠 Logic Behind the Game

To simulate the game:
1. Each cell is represented by a **logical variable**.
2. Cells with numbers generate **CNF constraints** based on nearby traps.
3. A **SAT solver** is used to deduce which cells are safe (gems) and which are traps.
4. The program compares multiple solving strategies:  
   - **SAT-based solving with `pysat`**
   - **Brute-force search**
   - **Backtracking**

## 🔧 Features

- 🧩 Automatic CNF generation from any grid-based input.
- 📦 `pysat` integration for solving CNFs.
- 🐌 Brute-force and 🧭 backtracking implementations for benchmarking.
- 🧪 Multiple test cases with varying grid sizes (from 5×5 to 20×20).
- ⏱️ Performance comparison (running time) between different algorithms.
