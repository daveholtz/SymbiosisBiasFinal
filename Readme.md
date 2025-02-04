# **Simulation Code for "Reducing Symbiosis Bias through Better A/B Tests of Recommendation Algorithms"**

## **Table of Contents**
1. [Repo Overview](#1-repo-overview)
2. [Simulation Details](#2-simulation-details)
3. [Installation & Usage](#3-installation--usage)
4. [Contact](#4-contact)

---

## **1. Repo Overview**

This repository contains replication code for the simulations found in "Reducing Symbiosis Bias through Better A/B Tests of
Recommendation Algorithms" (Brennan et al., ACM WWW 2025). The repo structure is described below:


```bash
.
├── functions/                        # Utility functions used in the simulation
│   
│   ├── fn_algorithm.py               # Implementation of recommendation algorithms
│   ├── fn_consumption.py             # Helper functions related to user consumption behavior
│   ├── fn_metrics.py                # Functions for measuring metrics (e.g., take-up rates)
│   ├── fn_set_env.py                # Environment parameter definitions
│   └── fn_simulation.py             # Standard simulation run (generic, not tied to specific methods)
|
├── results/                         # Output from simulation runs
│   
│   ├── TU_rates_VS_Cluster_Quality_final.csv      # Data for varying cluster_shuffle_percentage
│   ├── TU_rates_VS_Gamma_Pref_final.csv          # Data for varying gamma_pref
│   └── TU_rates_VS_Percentage_Treatment_final.csv # Data for varying treatment_percentage
|
├── plots/                           # Output from plotting script
│   
│   ├── bias_plot.pdf                # Plot showing bias of treatment effect estimates
│   ├── cluster_quality_plot.pdf     # Plot showing bias as a function of cluster quality
│   ├── gamma_pref_plot.pdf          # Plot showing bias as a function of gamma_pref
│   └── trt_pct_plot.pdf             # Plot showing bias as a function of treatment percentage
|
├── Simulation.ipynb                 # Main Jupyter Notebook to execute the simulation
|
├── generate_paper_plots.R           # Main R file to generate all simulation plots
|
└── README.md                        # Project documentation (this file)
```

---

## **2. Simulation Details**
### Parameters
Constants:
`B` = `n_sim` = Number of simulations  
`num_users` = Number of total users  
`num_items` = Number of total items

Variables:
`gamma_pref` = parameter for Dirichlet Distribution for user preferences
`gamma_item` = parameter for Dirichlet Distribution for item characteristics
`treatment_percentage` = percentage of users being assigned to the treatment group
`cluster_shuffle_percentage` = percentage of users being randomly shuffled to other groups

The simulation runs multiple iterations (denoted by `B`) to simulate user interactions with items.  
Users are assigned to two different recommendation algorithms (`algo_1` and `algo_2`), based on a random user assignment matrix.

### Simulation Loop (for Each Iteration)

In each simulation run, users are exposed to items over multiple periods. During each period, new items are introduced, and recommendation algorithms suggest items to users based on the available user data. This iterative process allows for the evaluation of algorithmic performance and interactions under different conditions.

### Methods

#### **Reference (Control Group)**
- `algo_1` and `algo_2` are identical recommendation algorithms.
- Both algorithms learn from the entirety of the user data, ensuring no differences in how they learn or perform.
- This serves as the **control group** for analyzing potential biases, as no bias is introduced by the learning process.

#### **Naive Approach**
- Both `algo_1` and `algo_2` learn from and act on the **same user data**.
- The algorithms influence each other through their interactions with the shared dataset, potentially introducing mutual interference and bias.

#### **Data-diverted Approach**
- `algo_1` and `algo_2` each keeps a separate interaction history for their own users, and learns from their own interaction history. 
- Users interact with the same pool of items.
- By keeping seperated interaction history, it tries to reduce the bias introduced. 
  
#### **User-Corpus Codiverted Approach**
- `algo_1` and `algo_2` learn from **disjoint subsets** of the user data, determined by `treatment_percentage` and \( 1 - `treatment_percentage` \).
- The interaction history is shared between both algorithms.

#### **Clustering-Based Approach**
- User data is divided into **clusters** based on predefined criteria.
- All users within a cluster are assigned the same recommendation algorithm.


#### Recommendation Process
After a certain number of `initial periods `, the recommendation algorithms generate recommendations for the users. Based on user assignments, either `algo_1` or `algo_2` provides the recommendations for each user.
##### Recommendation Algorithms
###### Item_based_CF
- An algorithm that recommends items most similar to the items that a user has
previously consumed.
###### User_based_CF
- An algorithm that recommends items consumed by the users most similar to the focal user.
###### Random
-  An algorithm that randomly recommends content to users.
###### Ideal
- An algorithm that recommends the available item to each user that will give them the highest utility.

#### Consumption Process
Users choose items to consume from the `recommended list` and from newly introduced items, influenced by utility scores. The `user-item interaction` is recorded, and previous consumption is tracked.

#### Evaluation
At the end of each simulation, the average "take-up" rate (how often users consumed the recommended items) is calculated for both algorithms.

#### Final Results
After all iterations, the simulation computes the average take-up rates and confidence intervals for both algorithms across all simulations.

---

## **3. Installation \& Usage**
Follow these steps to set up the project on your local machine. This includes cloning the repository, setting up a virtual environment, and installing dependencies.

To run the simulation from command line:
```bash
# Clone the repository to your local machine:
git clone <repository_url>
cd <repository_directory>

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install scikit-learn numpy scipy jupyter matplotlib pandas

# Install ipykernel and create a Jupyter kernel for the virtual environment:
pip install ipykernel
python3 -m ipykernel install --user --name=venv_symbiosis

# Set the environmental parameter and run the project
# You can execute the simulation directly from the command line using the following command. If environment variables are
# not set manually, default values will be used (GAMMA_PREF=1, GAMMA_ITEM=1, TREATMENT_PERCENT=0.5,
# CLUSTER_SHUFFLE_PERCENTAGE=0.0).
GAMMA_PREF=0.5 GAMMA_ITEM=0.5 TREATMENT_PERCENT=0.7 CLUSTER_SHUFFLE_PERCENTAGE=0.1 \
jupyter nbconvert --to python Simulation.ipynb --execute --ExecutePreprocessor.kernel_name=venv_symbiosis
```

Alternatively, you can open Simulation.ipynb in Jupyter Notebook via Anaconda. Make sure to update the environment parameters as needed within the notebook. Again, if environment variables are not set manually, default values will be used \(`GAMMA_PREF=1`, `GAMMA_ITEM=1`, `TREATMENT_PERCENT=0.5`, `CLUSTER_SHUFFLE_PERCENTAGE=0.0`\).

As a guide for setting environment variables, we tested the variables with the following values in our experiment:
- `GAMMA_PREF` :  [1, 3, 5, 7, 10, 15, 20, 50, 100]
- `TREATMENT_PERCENT` :  [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
- `CLUSTER_SHUFFLE_PERCENTAGE` :  [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]

---

## **4. Contact**

For questions about the code in this repository, please contact David Holtz (http://www.daveholtz.net).

### **Developed by:**

**Yahu Cong**  
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Profile-blue?logo=linkedin)](https://linkedin.com/in/yahu-cong-b52285297/) 
[![GitHub](https://img.shields.io/badge/GitHub-Profile-black?logo=github)](https://github.com/Yahu-Cong/)

**Yiwei Yu**  
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Profile-blue?logo=linkedin)](https://linkedin.com/in/yiwei-ivy-yu/) 
[![GitHub](https://img.shields.io/badge/GitHub-Profile-black?logo=github)](https://github.com/YiweiIvy/)

**David Holtz**  
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Profile-blue?logo=linkedin)](https://linkedin.com/in/david-holtz-00426220/) 
[![GitHub](https://img.shields.io/badge/GitHub-Profile-black?logo=github)](https://github.com/daveholtz/)

---
