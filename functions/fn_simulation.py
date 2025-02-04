from sklearn.metrics import silhouette_score
from sklearn.cluster import KMeans
import numpy as np
from functions.fn_consumption import *
from functions.fn_metrics import *


def run_simulation(params, user_item_utility, reserve_utilities,algo_1, algo_2):
    
    # Initialize results lists
    avg_c_algo_1_list = []
    avg_c_algo_2_list = []

    # Pre-generate user assignment matrix
    #np.random.seed(random_seed)
    user_assignments_matrix = np.random.randint(0, 2, (params.B, params.num_users)).astype(bool)
    
    # Number of new items in each period
    n_new = params.num_items_per_period

    for b in range(params.B):
        # Get user assignments for this simulation
        user_assignments = user_assignments_matrix[b]
        # Generate noise for all simulations and periods
        noise = np.random.normal(0, 1,(params.num_periods,params.num_users, params.num_periods * params.num_items_per_period))
        # Generate user-item interaction matrix
        interaction_matrix = np.zeros((params.num_users, params.num_items))

        # Record previous consumption
        prev_consumed_items = [[] for _ in range(params.num_users)]
        
        for t in range(params.num_periods):
            
            
            #### Introduce new goods
            new_items = np.repeat([list(range(t * n_new, (t + 1) * n_new))], params.num_users, axis=0)
            np.apply_along_axis(np.random.shuffle, 1, new_items)
            recommended_items = [[] for _ in range(params.num_users)]
            
            #### Recommendation step
            # Update the training data every training_frequency periods
            if t % params.training_frequency == 0 and t >= params.initial_periods:
                training_data = interaction_matrix[:, :(t * n_new)]
                recommended_items_1, consumed_items_1 = algo_1(training_data, noise[t,:, :(t * n_new)])
                recommended_items_2, consumed_items_2 = algo_2(training_data, noise[t,:, :(t * n_new)])
                
                # generate the actual recommendation list
                recommended_items = recommended_items_1.copy()
                recommended_items[user_assignments] = recommended_items_2[user_assignments]
                consumed_items = consumed_items_1.copy()
                consumed_items[user_assignments] = consumed_items_2[user_assignments]
            
            #### Consumption step
            # Simulate the chosen items for each user
            if t <  params.initial_periods:
                chosen_items = consume_item_all_users_loop(recommended_items, new_items, user_item_utility, None, reserve_utilities, params)
            else:
                chosen_items = consume_item_all_users_loop(recommended_items, new_items, user_item_utility, consumed_items, reserve_utilities, params)
           
            # Update the user-item interaction in interaction_matrix and prev_consumed_items
            for user_id, chosen_item in enumerate(chosen_items):
                prev_consumed_items[user_id].append(chosen_item)
                if chosen_item != -1:
                    interaction_matrix[user_id,chosen_item] = 1
        # Calculate the average take-up rate
        [avg_c_algo_1,avg_c_algo_2] = avg_take_up_rate_by_period(prev_consumed_items, user_assignments, params)
        avg_c_algo_1_list.append(avg_c_algo_1)
        avg_c_algo_2_list.append(avg_c_algo_2)
        if b < params.B:
            # Print the count of the simulation with replacement
            print(f"Simulation {b + 1} of {params.B} completed", end='\r', flush=True)
            with open(params.output_file, 'a') as f:
                f.write(f"Simulation {b + 1} of {params.B} completed\n")
        else:
            print(f"Simulation {b + 1} of {params.B} completed")
            with open(params.output_file, 'a') as f:
                f.write(f"Simulation {b + 1} of {params.B} completed\n")

    # Calculate the average [avg_c_algo_1, avg_c_algo_2] across simulations
    avg_c_algo_1 = np.mean(avg_c_algo_1_list, axis=0)
    avg_c_algo_2 = np.mean(avg_c_algo_2_list, axis=0)

    return avg_c_algo_1, avg_c_algo_2
