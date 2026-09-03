# Context-Aware CLI Agent

## Overview
A proactive command-line assistant that utilizes pattern recognition to predict user workflows.

## Features
- **Behavioral Learning**: Parses execution streams to build a state machine of user habits.
- **Frequency Analysis**: Uses nested default dictionaries to calculate probabilities of next commands.
- **Persistent Memory**: Saves context patterns to a local `cli_memory.json` file.
- **Proactive Suggestions**: Suggests highly probable commands based on historical execution contexts.

## Usage
```bash
python3 main.py
```
