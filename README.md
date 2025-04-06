# Interview Time Slot Matching System

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/UchihaSusie/match-time-slot/blob/main/run_in_colab.ipynb)


A sophisticated interview scheduling system that automatically coordinates interview times between candidates and recruiters across different time zones using multiple scheduling algorithms.

---

## Project Overview

This automated interview scheduling tool parses emails from candidates and recruiters, extracts availability and timezone information, and then uses various algorithms to find optimal interview slots. The system can handle users in different time zones and provides multiple scheduling strategies to meet different needs.

---

## 🚀 Quick Start with Google Colab

Want to try the system without any setup? You can instantly run this project in Google Colab:

- ✅ Zero Installation – Everything runs in the cloud
- ✅ One-Click Setup – Just run the first cell to clone the repository
- ✅ Multiple Test Options:
  - **Target Sample Test** – Run 5 pre-defined test cases with no input required
  - **Random Sample Test** – Generate customized test cases with your specified parameters
  - **Real-world Message Test** – Simulate actual email exchanges between candidates and recruiters

👉 Just click the "Open in Colab" button above and follow the instructions in the notebook!

---

## 🔑 Key Features

- Automatic parsing of availability information from emails
- Cross-timezone interview coordination
- Support for three different scheduling algorithms:
  - Basic bipartite matching
  - Greedy algorithm with priority matching
  - Network flow algorithm for maximum matching
- Interview time conflict detection and avoidance
- Customizable interview duration and quantity limits

---

## 🧠 System Architecture

### 📁 File Structure

```
match-time-slot/
├── algos/                        # Scheduling algorithm implementations
│   ├── bipartite.py              # Bipartite matching algorithm
│   ├── greedy.py                 # Greedy scheduling algorithm
│   └── networkflow.py            # Network flow-based scheduling algorithm
├── utils/                        # Utility functions
│   ├── message_parser.py         # Email message parser
│   ├── message_generator.py      # Test message generator
│   └── time_parser.py            # Time parsing utilities
└── tests/                        # Test scripts
    ├── target_sample_test.py     # Pre-defined test cases
    ├── random_sample_test.py     # Customizable random tests
    └── reward_message_test.py    # Real-world message simulation
```

---

## 🧩 Core Components

### 📬 Message Parser (`utils/message_parser.py`)

- Extracts key information from email text
- Identifies names, contact details, timezones, and available times

### 🧠 Scheduling Algorithms

- **Bipartite Matching** (`algos/bipartite.py`)  
  Basic time slot matching

- **Greedy Algorithm** (`algos/greedy.py`)  
  Prioritizes earlier time slots, supports real-time adjustments

- **Network Flow Algorithm** (`algos/networkflow.py`)  
  Uses Ford-Fulkerson algorithm for maximum matching

---

## ✅ Running Tests

```bash
# Test message parsing
python tests/reward_message_test.py

# Run predefined test cases
python tests/target_sample_test.py

# Large-scale random testing
python tests/random_sample_test.py
```

---

## 📊 Algorithm Comparison

| Algorithm          | Advantages                            | Disadvantages               | Use Cases                            |
| ------------------ | ------------------------------------- | --------------------------- | ------------------------------------ |
| Bipartite Matching | Simple, fast                          | Lower optimization level    | Small-scale scheduling               |
| Greedy Algorithm   | Efficient, supports real-time updates | May not be globally optimal | Dynamic adjustments, real-time needs |
| Network Flow       | Finds maximum matches                 | Higher computational cost   | Maximizing interview count           |

---

## 🌍 Timezone Handling

- All time comparisons are performed in UTC
- Original timezone information is preserved for display
- Supports multiple timezone formats (EST, PST, CST, etc.)

---

## 🛠️ Installation Guide

```bash
# Clone the repository
git clone https://github.com/UchihaSusie/match-time-slot.git
cd match-time-slot

# Install dependencies
pip install -r requirements.txt
```

---

## 🚧 Future Improvements

- Add a user interface
- Support more input formats
- Integrate calendar systems
- Add more advanced scheduling objectives
- Support stricter constraints (e.g. blackout times)

---

## 🤝 Contributing

Contributions are welcome! Feel free to improve the code or suggest enhancements.

```bash
# Fork the repository
# Create a feature branch
git checkout -b feature/amazing-feature

# Commit your changes
git commit -m 'Add some amazing feature'

# Push to GitHub
git push origin feature/amazing-feature

# Create a Pull Request
```
