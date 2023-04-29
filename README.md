# Transformer-Polyp-Tracker

This repository hosts the **Transformer-Polyp-Tracker**, a machine learning project that uses PyQT and PyTorch to accomplish real-time detection of polyps in colonic videos.

## Installation

To start using the software, follow these steps:

1. Clone this repository to download the project files: `git clone https://github.com/alancarlosml/transformer-polyp-tracker-qt.git`
2. Navigate to the project directory using the command line: `cd transformer-polyp-tracker-qt`
3. Create a new virtual environment to keep the project's dependencies separate from other Python projects on your computer: `virtualenv venv` or `conda env create --name venv` (Conda)
4. Activate the virtual environment to use the packages installed in the environment: `source venv/bin/activate` (Linux) or `venv\Scripts\activate` (Windows). For Conda, `conda activate venv`
5. Install the required packages: `pip install -r requirements.txt`
6. Download the pre-trained DETR weights from the following link and save them to the "model" folder in the root directory of this repository: https://drive.google.com/drive/folders/1k0LuROFW1W35oe392RMuAivo6uI9duFZ?usp=share_link

## Usage

### Running the Application

1. Open a terminal/command prompt window
2. Navigate to the project directory: `cd transformer-polyp-tracker-qt`
3. Run the following command: `python main.py`
4. Once the GUI opens, click the "Load Weights" button and select the DETR weights file you downloaded during installation.
5. Select the colonoscopy video you want to process by clicking the "Start" button. You can find some video samples in the "input" folder. Progress will be displayed in the status bar and the progress bar.
6. Once processing is complete, a new video will be saved to the "media" folder in the root directory of this repository.
7. To view the processed video, click the "File > History" menu item and select the video you want to view. Click the "Play" button to view the video in a new window.

## Acknowledgements

This work was supported by Coordenação de Aperfeiçoamento de Pessoal de Nível Superior (CAPES), Brazil - Finance Code 001, Conselho Nacional de Desenvolvimento Científico e Tecnológico (CNPq), Brazil, and Fundação de Amparo à Pesquisa e ao Desenvolvimento Científico e Tecnológico do Maranhão (FAPEMA), Brazil.
