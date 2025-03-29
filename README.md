# ZynTracker

A simple, elegant tracking application for daily Zyn consumption. Built with Python and PySide6.

![ZynTracker Screenshot](screenshots/zyn-tracker-screenshot.png)
*(Add your screenshot here)*

## Features

- **Sleek circular UI**: Minimalist design with a custom background image
- **Daily tracking**: Automatically tracks consumption by date
- **Persistent storage**: Saves your data between sessions
- **Always on top**: Window stays visible for easy access
- **Draggable**: Position the app anywhere on your screen

## Requirements

- Python 3.6+
- PySide6
- A background image file named `zyn_can_background.png` in the application directory

## Installation

1. Clone this repository or download the source code
2. Install required packages:
   ```
   pip install PySide6
   ```
3. Add your background image as `zyn_can_background.png` in the project directory
4. Run the application:
   ```
   python main.py
   ```

## Usage

- The counter displays your daily Zyn consumption
- Use the **+** button to increase the count
- Use the **–** button to decrease the count
- Click and drag anywhere to move the window
- Click the **✕** button to close the application

The application automatically saves your data between sessions and resets the counter each day.

## Project Structure

- `main.py` - Main application code
- `zyn_data.json` - Data storage file (created automatically)
- `zyn_can_background.png` - Background image file (needs to be provided)

## Technologies Used

- **Python**: Core programming language
- **PySide6**: Qt bindings for Python to create the GUI
- **JSON**: Data storage format

## Future Improvements

- Weekly and monthly statistics
- Usage trends visualization
- Customizable background images
- Setting consumption goals
