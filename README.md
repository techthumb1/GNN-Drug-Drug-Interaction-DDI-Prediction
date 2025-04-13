# GNN-Drug-Drug-Interaction-DDI-Prediction

The GNN-Drug-Drug-Interaction-DDI-Prediction repository contains code and data for predicting drug-drug interactions (DDIs) using graph neural networks (GNNs). The project is developed for the purpose of advancing research in drug discovery and safety by leveraging machine learning techniques.

## Table of Contents

- [GNN-Drug-Drug-Interaction-DDI-Prediction](#gnn-drug-drug-interaction-ddi-prediction)
  - [Table of Contents](#table-of-contents)
  - [Introduction](#introduction)
  - [Installation](#installation)
  - [Usage](#usage)
  - [Data](#data)
  - [Results](#results)
  - [License](#license)
  - [Contributing](#contributing)
  - [Acknowledgments](#acknowledgments)
  - [Contact](#contact)
  - [References](#references)

## Introduction

Drug-drug interactions (DDIs) can lead to adverse drug reactions, making it crucial to predict potential interactions between drugs. This project utilizes graph neural networks (GNNs) to model the relationships between drugs and predict DDIs.
The GNN architecture is designed to capture the complex interactions between drugs based on their chemical structures and known interactions.

## Installation

To install the required dependencies, you can use pip. Make sure you have Python 3.6 or higher installed.

```bash
pip install -r requirements.txt
```

## Usage

To run the DDI prediction model, you can use the following command:

```bash
python main.py --config config.yaml
```

This will load the configuration from `config.yaml` and execute the training and evaluation process.
You can modify the configuration file to adjust hyperparameters, model architecture, and other settings.

## Data

The dataset used for training and evaluation is available in the `data` directory. The data is organized into training, validation, and test sets.
The dataset contains information about drug pairs and their interaction labels (interacting or non-interacting).
The data format is as follows:

- `train.csv`: Training set containing drug pairs and their interaction labels.
- `val.csv`: Validation set containing drug pairs and their interaction labels.
- `test.csv`: Test set containing drug pairs and their interaction labels.
- `drug_features.csv`: Drug features used for GNN input.
- `interaction_graph.pkl`: Preprocessed interaction graph used for GNN training.
- `drug_graph.pkl`: Preprocessed drug graph used for GNN training.
- `drug_graph_1.pkl`: Preprocessed drug graph used for GNN training.
- `drug_graph_2.pkl`: Preprocessed drug graph used for GNN training.
- `drug_graph_3.pkl`: Preprocessed drug graph used for GNN training.
- `drug_graph_4.pkl`: Preprocessed drug graph used for GNN training.

## Sources

- [Drug Bank] [https://www.drugbank.ca/]
- [BioKG] [https://biokg.org/]
- [Hetionet] [https://www.hetio.net/]
- [ChEMBL] [https://www.ebi.ac.uk/chembl/]
- [PubChem] [https://pubchem.ncbi.nlm.nih.gov/]
- [STITCH] [http://stitch.embl.de/]
- [BindingDB] [https://www.bindingdb.org/bind/index.jsp]
- [DrugCentral] [https://drugcentral.org/]
- [Drug Interaction Database] [https://www.druginteractiondatabase.com/]
- [Drug Interaction Checker] [https://www.druginteractionchecker.com/]

## Results

The results of the DDI prediction model are saved in the `results` directory. The evaluation metrics include accuracy, precision, recall, and F1-score.
The results are saved in a CSV file format for easy analysis.
The results are also visualized using various plots to show the performance of the model on the validation and test sets.
The results include:

- Accuracy: The overall accuracy of the model on the test set.
- Precision: The precision of the model on the test set.
- Recall: The recall of the model on the test set.
- F1-score: The F1-score of the model on the test set.
- ROC-AUC: The ROC-AUC score of the model on the test set.
- PR-AUC: The PR-AUC score of the model on the test set.
- Confusion Matrix: The confusion matrix of the model on the test set.
- Classification Report: The classification report of the model on the test set.
- Training Loss: The training loss of the model during training.
- Validation Loss: The validation loss of the model during training.
- Training Accuracy: The training accuracy of the model during training.
- Validation Accuracy: The validation accuracy of the model during training.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
