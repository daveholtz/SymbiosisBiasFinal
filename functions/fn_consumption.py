import numpy as np

def consume_item_all_users_loop(recommended_items_all_users, new_items_all_users, user_item_utility, reserve_utilities, param):
    """
    This function simulates item consumption for all users.

    Parameters:
    recommended_items_all_users (numpy array): 2D array of recommended items for all users.
    new_items_all_users (numpy array): 2D array of new items for all users.
    user_item_utility (numpy array): Matrix of user-item utility values.
    reserve_utilities (numpy array): Array of reserve utilities for each user.
    param (object): An instance of a class containing model parameters (e.g., number of users).

    Returns:
    chosen_items_all_users (list): List of IDs of items chosen by each user.
    """

    num_users = param.num_users
    chosen_items_all_users = [-1] * num_users

    for user_id in range(num_users):
        # Directly pass recommended items without filtering since consumed items are already excluded
        chosen_items_all_users[user_id] = consume_item(user_id, recommended_items_all_users[user_id], new_items_all_users[user_id], user_item_utility, reserve_utilities)

    return chosen_items_all_users

def consume_item_all_users_loop_user_corpus(recommended_items_all_users, new_items_all_users, user_item_utility, reserve_utilities, param, item_assignments, user_assignments):
    """
    This function simulates item consumption for all users for under user-corpus co-diverted method.
    It calls consume_item_user_corpus() instead of consume_item().

    Parameters:
    recommended_items_all_users (numpy array): 2D array of recommended items for all users.
    new_items_all_users (numpy array): 2D array of new items for all users.
    user_item_utility (numpy array): Matrix of user-item utility values.
    reserve_utilities (numpy array): Array of reserve utilities for each user.
    param (object): An instance of a class containing model parameters (e.g., number of users).
    user_assignments (numpy array): Matrix of algorithm assignments for each user.
    reserve_utilities (numpy array): Matrix of algorithm assignments for each item.

    Returns:
    chosen_items_all_users (list): List of IDs of items chosen by each user.
    """

    num_users = param.num_users
    chosen_items_all_users = [-1] * num_users
    
    for user_id in range(num_users):
        # Directly pass recommended items without filtering since consumed items are already excluded
        chosen_items_all_users[user_id] = consume_item_user_corpus(user_id, recommended_items_all_users[user_id], new_items_all_users[user_id], user_item_utility, reserve_utilities, item_assignments, user_assignments)

    return chosen_items_all_users



def consume_item(user_id, recommended_items, new_items, user_item_utility, reserve_utilities):
    """
    Choose the item with the highest utility.
    Consume the chosen item.
    Returns the chosen item.
    
    Parameters:
    user_id (int): ID of the user who consumes the item.
    recommended_items (list): List of recommended item IDs.
    new_items (list): List of new item IDs.
    user_item_utility (numpy array): Matrix of user-item utility values.
    reserve_utilities (numpy array): Array of reserve utilities for each user.
    
    
    Returns:
    chosen_item (int): ID of the item with the highest observed utility.
    """
    # Interleave recommended items with new items
    # Prepare a list to interleave new_items and recommended_items
    total_len = len(recommended_items) + len(new_items)
    interleaved_items = np.empty(total_len, dtype=int)
    if len(recommended_items) ==0:
        interleaved_items = new_items
    else:
        n_news = len(new_items)
        interleaved_items[1:2*n_news:2] = new_items
        interleaved_items[0:2*n_news:2] = recommended_items[:n_news]
        interleaved_items[2*n_news:] = recommended_items[n_news:]

    # Calculate observed utility
    observed_utility = user_item_utility[user_id, interleaved_items] * ((1 + np.arange(len(interleaved_items))) ** -0.8)
    max_index = np.argmax(observed_utility)

    if observed_utility[max_index] > reserve_utilities[user_id]:
        chosen_item = interleaved_items[max_index]
    else:
        chosen_item = -1
    return chosen_item

def consume_item_user_corpus(user_id, recommended_items, new_items, user_item_utility, reserve_utilities, item_assignments, user_assignments):
    """
    Choose the item with the highest utility.
    Consume the chosen item.
    Returns the chosen item.
    In user-corpus co-diverted method, users only consume items assigned to the same algorithm (controlled or treated) as them.
    
    Parameters:
    user_id (int): ID of the user who consumes the item.
    recommended_items (list): List of recommended item IDs.
    new_items (list): List of new item IDs.
    user_item_utility (numpy array): Matrix of user-item utility values.
    reserve_utilities (numpy array): Array of reserve utilities for each user.
    user_assignments (numpy array): Matrix of algorithm assignments for each user.
    reserve_utilities (numpy array): Matrix of algorithm assignments for each item.
    
    Returns:
    chosen_item (int): ID of the item with the highest observed utility.
    """

    # Ensure recommended_items and new_items are numpy arrays
    recommended_items = np.array(recommended_items)
    new_items = np.array(new_items)

    # Get user assignment
    user_assignment = user_assignments[user_id]

    # Create mask for recommended_items based on item assignments
    item_assignments_array = np.array([item_assignments[item] for item in recommended_items])
    mask = (item_assignments_array == user_assignment)
    # Select recommended items with the same assigned algorithm as the user
    recommended_items = recommended_items[mask]

    # Create mask for new_items based on item assignments
    item_assignments_array = np.array([item_assignments[item] for item in new_items])
    mask = (item_assignments_array == user_assignment)
    # Select new items with the same assigned algorithm as the user
    new_items = new_items[mask]
    
    # Prepare a list to interleave new_items and recommended_items
    total_len = len(recommended_items) + len(new_items)
    interleaved_items = np.empty(total_len, dtype=int)
    if len(recommended_items) ==0:
        interleaved_items = new_items
    else:
        n_news = len(new_items)
        min_len = min(len(recommended_items), len(new_items))  # find the minimum length to interleave properly
        interleaved_items[1:2*min_len:2] = new_items[:min_len]
        interleaved_items[0:2*min_len:2] = recommended_items[:min_len]

        # Handle remaining items if lengths are unequal
        if len(new_items) > min_len:
            interleaved_items[2*min_len:] = new_items[min_len:]
        elif len(recommended_items) > min_len:
            interleaved_items[2*min_len:] = recommended_items[min_len:]
        

    # If no items are left after filtering, return -1
    if len(interleaved_items) == 0:
        return -1

    # Calculate observed utility
    observed_utility = user_item_utility[user_id, interleaved_items] * ((1 + np.arange(len(interleaved_items))) ** -0.8)
    max_index = np.argmax(observed_utility)

    if observed_utility[max_index] > reserve_utilities[user_id]:
        chosen_item = interleaved_items[max_index]
    else:
        chosen_item = -1
    return chosen_item
