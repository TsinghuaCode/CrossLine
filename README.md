# Line Matching Visualizer

A graphical user interface (GUI) application for visualizing line matching problems on a grid, using heuristic search algorithms to find paths for multiple lines while avoiding collisions. The application supports two modes with different cost functions and allows users to interactively set up the problem and observe the search process.


## Table of Contents

- [Line Matching Visualizer](#line-matching-visualizer)
  - [Table of Contents](#table-of-contents)
  - [Features](#features)
  - [Installation](#installation)
  - [Usage](#usage)
  - [Code Structure](#code-structure)
  - [Algorithm Explanation](#algorithm-explanation)
  - [Contributing](#contributing)


## Features

1. **Interactive Grid Setup**:
   - Define grid size (`n`, 2-10) and number of line pairs (`m`, 1-10).
   - Input start and end coordinates for each line pair.

2. **Two Modes**:
   - **Mode 1**: Basic cost function (movement cost = 1 for each step).
   - **Mode 2**: Includes penalty for direction changes (additional cost of 2 when a line changes direction).

3. **Visualization**:
   - Real-time animation of the search process on a canvas.
   - Different colors for each line pair.
   - Status bar showing current step and path cost.

4. **Control Options**:
   - Start, pause, and reset the search.
   - Adjust animation speed with a slider.

5. **Heuristic Search**:
   - Uses a priority queue (A*-like algorithm) with configurable heuristic functions:
     - **Null Heuristic** (for uniform cost search).
     - **Manhattan Distance** (sum of Manhattan distances for all unfinished lines).
     - **Obstacle-Aware Heuristic** (Manhattan distance + obstacle penalties for mode 2).


## Installation

1. **Prerequisites**:
   - Python 3.6+
   - `numpy` (for array operations, though minimally used here)

2. **Install Dependencies**:
   ```bash
   pip install numpy
   ```

3. **Run the Application**:
   ```bash
   python CrossLine.py
   ```


## Usage

1. **Input Setup**:
   - **Grid Settings**: Enter `n` (grid size) and `m` (number of line pairs).
   - **Coordinates**: For each line pair, input start and end coordinates (1-based index).
   - **Mode**: Select between Mode 1 and Mode 2.

2. **Controls**:
   - **Apply Settings**: Validate inputs and initialize the grid.
   - **Start**: Begin the search algorithm.
   - **Pause/Resume**: Toggle search animation.
   - **Reset**: Clear the canvas and restart the setup.
   - **Speed Slider**: Adjust animation speed (higher value = faster).

3. **Visualization**:
   - The canvas shows the grid, line start/end points, and paths.
   - Circles represent start points, rectangles represent end points.
   - Dashed lines indicate the current path of active lines.


## Code Structure

- **`ModernVisualizer` (GUI Class)**:
  - Manages the Tkinter UI, including input forms, buttons, canvas, and status bar.
  - Handles thread communication for animation using a queue.

- **Search Components**:
  - **`Node`**: Represents a state in the search, including grid configuration and path cost.
  - **`MatchProblem` (Subclass of `Problem`)**: Defines the problem specifics, such as valid moves, goal check, and cost functions.
  - **`PriorityQueue` and `Set`**: Data structures for managing open and closed states in the search.

- **Heuristics & Path Generation**:
  - `h_function_method1`: Basic Manhattan distance heuristic.
  - `h_function_method2`: Manhattan distance plus obstacle penalties (used in mode 2).
  - Path generation functions for horizontal/vertical movement.


## Algorithm Explanation

- **Search Algorithm**:
  - Uses a priority queue to explore states, ordered by a combination of path cost (`g(n)`) and heuristic value (`h(n)`).
  - `g(n)` includes movement cost and (in mode 2) a penalty for direction changes.
  - `h(n)` estimates the remaining cost to the goal, using Manhattan distance or obstacle-aware calculations.

- **State Representation**:
  - `(grid, lines, active_line)`: 
    - `grid`: 2D array marking occupied cells by line indices.
    - `lines`: List of `[start, end]` coordinates for each line.
    - `active_line`: Index of the line being moved in the current step.

- **Goal Condition**:
  - All lines have their start and end coordinates matched (no active lines left).


## Contributing

1. **Issue Tracking**: Report bugs or suggest features in the [Issues](https://github.com/your-username/line-matching-visualizer/issues) section.
2. **Pull Requests**: Submit PRs for bug fixes, improvements, or new features. Ensure code is well-documented and follows PEP8 standards.


**Zhiqi Chen** | [GitHub](https://github.com/TsinghuaCode) | [Email](zq-chen23@mails.tsinghua.edu.cn)
