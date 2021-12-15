# Conway's Game-of-Life
Conway’s Game of Life - HCI 2021-2022 Programming Assignment

## Overview
The Game of Life was invented in 1970 by the British mathematician John Horton Conway. He developed an interest in a problem which was made evident in the 1940’s by mathematician John von Neumann, who aimed to find a hypothetical machine that had the ability to create copies of itself and was successful when he discovered a mathematical model for such a machine with very complicated rules on a rectangular grid. Thus, the Game of Life was Conway’s way of simplifying von Neumann’s ideas. It is the best-known example of a cellular automaton which is any system in which rules are applied to cells and their neighbors in a regular grid. Martin Gardner popularized the Game of Life by writing two articles for his column “Mathematical Games” in the journal Scientific American in 1970 and 1971.

## Rules of the Game
The game is played on a two-dimensional grid (or board). Each grid location is either empty or populated by a single cell. A location’s **neighbors** are any cells in the surrounding **eight adjacent locations**. The simulation of starts from an **initial state** of populated locations and then **progresses through time**. The evolution of the board state is governed by a few simple rules:
1. Each populated location with one or zero neighbors dies (from loneliness).
2. Each populated location with four or more neighbors dies (from overpopulation).
3. Each populated location with two or three neighbors survives.
4. Each unpopulated location that becomes populated if it has exactly **three** populated neighbors.
5. All updates are performed simultaneously **in parallel**.

This figure illustrates the rules for cell death, survival, and birth:

## Credits
- Icons taken by [iconmonstr](https://iconmonstr.com/).
- Programming assignment of Human Computer Interaction course by [Andrew D. Bagdanov](http://www.micc.unifi.it/bagdanov/).
