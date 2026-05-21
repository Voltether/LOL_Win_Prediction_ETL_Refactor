# Modular 3 - League of Legends Match Predictor

Data engineering + machine learning project focused on extracting,
processing, and modeling ranked League of Legends match data using
the Riot Games API.

The project includes a modular ETL pipeline, feature engineering,
SQLite/PostgreSQL integration, and logistic regression modeling
for match outcome prediction.

## Overview

This project started as an exploratory Jupyter Notebook and is 
currently being refactored into a modular Python project.

The goal is to:
- Collect ranked match data from the Riot API
- Build structured datasets
- Store processed data in SQL databases
- Train predictive models
- Analyze in-game metrics and their impact on match outcomes

Current focus:
- ETL refactor
- Database integration
- Reproducibility
- Feature engineering cleanup

## Features

- Riot Games API integration
- Ranked match extraction
- Feature engineering from timeline data
- Gold differential analysis
- Logistic regression modeling
- ROC AUC evaluation
- SQLite/PostgreSQL support
- YAML-based configuration
- Modular ETL structure
- Visualization pipeline

## Tech Stack

- Python
- Pandas
- Scikit-learn
- SQLAlchemy
- SQLite
- PostgreSQL
- YAML
- Matplotlib
- Jupyter Notebook
- Git

## Project Structure

```text
project_root/
│
├── data/
│   ├── raw/
│   ├── interim/
│   ├── processed/
│   └── database/
│
├── notebooks/
│
├── scripts/
│
├── src/
│   ├── config/
│   ├── data/
│   ├── features/
│   ├── models/
│   └── visualization/
│
├── config.yaml
├── requirements.txt
└── README.md
```

```md   
## Current Status

The project is currently under active refactor from a notebook-based
workflow into a reproducible Python package structure.

ML results and model evaluation refactor in process as well as
CSV to SQL migration

Completed:
- Match extraction
- Feature generation
- Initial ML workflow
- SQLite integration

In progress:
- Full ETL modularization
- Database abstraction
- Training pipeline cleanup
- Improved reproducibility
