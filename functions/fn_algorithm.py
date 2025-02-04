from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from scipy.sparse import csr_matrix


def User_based_CF(training_data, noise):
    """
    Recommend items to all users based on a user-based collaborative filtering algorithm.

    Parameters:
    interaction_matrix (numpy array): Matrix of user-item interactions.
    params (Param): An instance of the Param class.
    noise (numpy array): An array of random noise used to break ties.

    Returns:
    ranked_items_all_users (numpy array): 2D array of ranked item IDs recommended to each user.
    consumed_items_all_users (boolean matrix): An matrix indicating whether each user has consumed each item in the recommendation list.
    """
    
    noise_copy = noise.copy()
    # Convert training_data to a sparse matrix
    training_data_sparse = csr_matrix(training_data)

    # Compute user similarities matrix
    user_similarities = training_data_sparse @ training_data_sparse.T
    
    # Convert to LIL for efficient modification
    user_similarities = user_similarities.tolil()
    user_similarities.setdiag(0)  # Exclude the user from their own recommendations
    # Convert back to CSR for efficient arithmetic operations
    user_similarities = user_similarities.tocsr()
    
    # Calculate the sum of interactions of top similar users for all items
    item_scores_all_users = (training_data_sparse.T).astype(float) @ user_similarities

    # Convert item_scores_all_users back to a dense matrix for indexing
    item_scores_all_users = item_scores_all_users.toarray()
    # Exclude items each user has already interacted with
    already_interacted = training_data > 0
    item_scores_all_users[already_interacted.T] = -np.inf

    # Sort items by item scores and noise in descending order for each user
    ranked_items_all_users = np.lexsort((noise_copy.T, item_scores_all_users), axis=0)[::-1,].T

    # Create a boolean matrix indicating whether each user has consumed each item in the recommendation list
    rows = np.arange(already_interacted.shape[0])[:, None]
    consumed_items_all_users = already_interacted[rows, ranked_items_all_users]
    
    return ranked_items_all_users


def Item_based_CF(training_data, noise):
    """
    Recommend items to all users based on an item-based collaborative filtering algorithm using cosine similarity.

    Parameters:
    training_data (numpy array): Matrix of user-item interactions.
    noise (numpy array): An array of random noise used to break ties.

    Returns:
    ranked_items_all_users (numpy array): 2D array of ranked item IDs recommended to each user.
    consumed_items_all_users (boolean matrix): An matrix indicating whether each user has consumed each item in the recommendation list.
    """
    noise_copy = noise.copy()
    
    # Calculate the item similarity matrix using cosine similarity
    item_similarity_matrix = cosine_similarity(training_data.T)

    # Calculate the users' predicted interaction scores for all items
    predicted_interaction_scores = (item_similarity_matrix @ training_data.T)

    # Exclude items each user has already interacted with
    already_interacted = training_data > 0

    predicted_interaction_scores[already_interacted.T] = -np.inf
    
    # Sort items by item scores and noise in descending order for each user
    ranked_items_all_users = np.lexsort((noise_copy.T, predicted_interaction_scores), axis=0)[::-1,].T
    
    # Create a boolean matrix indicating whether each user has consumed each item in the recommendation list
    rows = np.arange(already_interacted.shape[0])[:, None]
    consumed_items_all_users = already_interacted[rows, ranked_items_all_users]

    
    return ranked_items_all_users


def Random_alg(training_data, noise):
    """
    Recommend items to all users based on a random recommendation strategy.

    Parameters:
    interaction_matrix (numpy array): Matrix of user-item interactions.
    noise (numpy array): An array of random noise used to break ties.

    Returns:
    ranked_items_all_users (numpy array): 2D array of ranked item IDs recommended to each user.
    consumed_items_all_users (boolean matrix): An matrix indicating whether each user has consumed each item in the recommendation list.
    """
    noise_copy = noise.copy()

    # Sort items by noise for each user
    ranked_items_all_users = np.argsort(noise_copy, axis=1)
    
    # Exclude items each user has already interacted with
    already_interacted = training_data > 0
   
    # Create a boolean matrix indicating whether each user has consumed each item in the recommendation list
    rows = np.arange(already_interacted.shape[0])[:, None]
    consumed_items_all_users = already_interacted[rows, ranked_items_all_users]

    return ranked_items_all_users

def Ideal_alg(training_data, user_item_utility, noise):
    """
    Recommend items to all users based on the highest utility among unconsumed items, and then consumed items.

    Parameters:
    interaction_matrix (numpy array): Matrix of user-item interactions.
    user_item_utility (numpy array): Matrix of user-item utility values.
    noise (numpy array): An array of random noise used to break ties.

    Returns:
    ranked_items_all_users (numpy array): 2D array of ranked item IDs recommended to each user.
    consumed_items_all_users (boolean matrix): An matrix indicating whether each user has consumed each item in the recommendation list.
    """
    noise_copy = noise.copy()
    # Initialize ranked items with infinities
    ranked_items_all_users = np.full_like(training_data, np.inf)

    # Get the list of items not yet interacted with by each user
    unconsumed_items = training_data == 0

    # Rank the unconsumed items by utility for each user
    utility = user_item_utility[:,:np.shape(unconsumed_items)[1]].copy()
    utility[~unconsumed_items] = -np.inf
    ranked_unconsumed_items = np.argsort(utility, axis=1)[:, ::-1]

    # Get the list of items already consumed by each user
    consumed_items = ~unconsumed_items

    # Rank the consumed items by noise for each user
    noise_copy[~consumed_items] = -np.inf
    ranked_consumed_items = np.argsort(noise_copy, axis=1)[:, ::-1]

    # Combine the lists, with unconsumed items first
    num_users, num_items = training_data.shape
    for user_id in range(num_users):
        num_unconsumed = unconsumed_items[user_id].sum()
        ranked_items_all_users[user_id, :num_unconsumed] = ranked_unconsumed_items[user_id, :num_unconsumed]
        ranked_items_all_users[user_id, num_unconsumed:] = ranked_consumed_items[user_id, :num_items-num_unconsumed]
    
    ranked_items_all_users = ranked_items_all_users.astype(int)

    # Create a boolean matrix indicating whether each user has consumed each item in the recommendation list
    rows = np.arange(consumed_items.shape[0])[:, None]
    consumed_items_all_users = consumed_items[rows, ranked_items_all_users]
    
    return ranked_items_all_users