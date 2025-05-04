# From metal ores to financial risk: a macro-evolutionary model of energy transition with energy, financial and commodity markets

Copyright (c) 2024 Taras Kryvyy

## Overview
This repository contains the source code and documentation for my PhD project, which focuses on developing a macro-evolutionary agent-based model to explore the material intensity of low-carbon energy transition and its interactions with macro-financial stability. The model integrates elements from commodity markets, financial stability, and climate-related macro-financial risks to provide insights into the dynamics of energy and material sectors within an evolving economy.

## Model Components
The model consists of the following sectors:
- Final Good Sector: Represents goods consumed by households.
- Energy Sector: Includes renewable energy and fossil-fuel-based energy consumed by final good firms.
- Materials Sector: Extracts ores from metal ore deposits and processes them into materials that are consumed by capital firms.
- Capital Sectors: Provide capital required for producing final goods, renewable energy, fossil-fuel-based energy, and materials.
- Banking Sector: Finances capital investments and short-term liquidity needs.

### Flow of goods and services 
<img width="420" alt="image" src="https://github.com/user-attachments/assets/6dccbc11-0a9e-468e-b559-dcd273e1ef2b"> 

### Money flow
<img width="600" alt="image" src="https://github.com/user-attachments/assets/4504ecc7-cafd-43e7-800a-026ed98ea694">


## Installation
To run the model, follow these steps:
1. Clone the repository to your local machine.
2. Install the required dependencies listed in `requirements.txt`.
3. Run the main model script, `start.py`, using your preferred Python interpreter.

## Usage
- Modify baseline model parameters in `parameters.py` and scenario parameters in `scenarios.py`  to explore different scenarios.
- Analyze simulation results using  `scenario_plotting.py`.

## Contribution Guidelines
Contributions to the model are welcome! If you'd like to contribute, please follow these guidelines:
- Fork the repository and create a new branch for your feature or bug fix.
- Make your changes and test thoroughly.
- Submit a pull request detailing the changes you've made and any relevant information.

## Contact
For questions, feedback, or collaboration opportunities, please contact:
- [Taras Kryvyy](mailto:taras.kryvyi@outlook.com)

## License
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
