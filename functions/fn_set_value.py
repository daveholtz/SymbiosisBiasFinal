import numpy as np

def generate_user_preferences(params):
    """
    Generates user preferences using Dirichlet distributions.

    Parameters:
    - params (Param): An instance of the Param class.

    Returns:
    - rho_u (np.ndarray): A 2D NumPy array of shape (params.num_users, params.K) representing
      the user preferences for each category or component. The values are random 
      floats between 0 and 1, generated using Dirichlet distributions.
    """
    # Generate mu_rho and rho_u using Dirichlet distributions
    mu_rho = 10 * np.random.dirichlet([1] * params.K)
    rho_u = np.random.dirichlet(mu_rho, params.num_users)

    return rho_u

def generate_user_preferences_cluster(params):
    """
    Generates user preferences using Dirichlet distributions. The realized values are
    concentrated around four randomly selected corners of the simplex.

    Parameters:
    - params (Param): An instance of the Param class.

    Returns:
    - rho_u (np.ndarray): A 2D NumPy array of shape (params.num_users, params.K) representing
      the user preferences for each category or component. The values are random 
      floats between 0 and 1, generated using Dirichlet distributions.
    """
    # Randomly select four corners
    corners = np.random.choice(params.K, size=4, replace=False)

    # Allocate space for the user preferences
    rho_u = np.zeros((params.num_users, params.K))

    # Concentration parameter (alpha) for Dirichlet distribution
    alpha_high = params.gamma_pref
    alpha_low = 1
    alpha = [alpha_low] * params.K
    
    # Allocate space for the group assignments
    group = np.zeros(params.num_users, dtype=int)
    
    # Generate user preferences
    for i in range(params.num_users):
        # Randomly choose one of the four corners
        corner = np.random.choice(corners)
        alpha[corner] = alpha_high  # Set the alpha parameter for the chosen corner to be high
        rho_u[i, :] = np.random.dirichlet(alpha)
        alpha[corner] = alpha_low  # Reset the alpha parameter for the chosen corner
        group[i] = corner  # Assign group
        
    if params.pref_group == True:
        return rho_u, group
    return rho_u

def generate_user_preferences_cluster_with_size(params, cluster_size):
    """
    Generates user preferences using Dirichlet distributions. The realized values are
    concentrated around four randomly selected corners of the simplex.

    Parameters:
    - params (Param): An instance of the Param class.

    Returns:
    - rho_u (np.ndarray): A 2D NumPy array of shape (params.num_users, params.K) representing
      the user preferences for each category or component. The values are random 
      floats between 0 and 1, generated using Dirichlet distributions.
    """
    # Randomly select four corners
    corners = np.random.choice(params.K, size=cluster_size, replace=False)

    # Allocate space for the user preferences
    rho_u = np.zeros((params.num_users, params.K))

    # Concentration parameter (alpha) for Dirichlet distribution
    alpha_high = params.gamma_pref
    alpha_low = 1
    alpha = [alpha_low] * params.K
    
    # Allocate space for the group assignments
    group = np.zeros(params.num_users, dtype=int)
    
    # Generate user preferences
    for i in range(params.num_users):
        # Randomly choose one of the four corners
        corner = np.random.choice(corners)
        alpha[corner] = alpha_high  # Set the alpha parameter for the chosen corner to be high
        rho_u[i, :] = np.random.dirichlet(alpha)
        alpha[corner] = alpha_low  # Reset the alpha parameter for the chosen corner
        group[i] = corner  # Assign group
        
    if params.pref_group == True:
        return rho_u, group
    return rho_u


def generate_item_char(params):
    """
    Generates item characteristics using Dirichlet distributions.

    Parameters:
    - params (Param): An instance of the Param class.

    Returns:
    - rho_alpha (np.ndarray): A 2D NumPy array of shape (params.num_items, params.K) representing 
      the item characteristics for each category or component. The values are 
      random floats between 0 and 1, generated using Dirichlet distributions.
    """
    # Generate mu_alpha and rho_alpha using Dirichlet distributions
    mu_alpha = 0.1 * np.random.dirichlet([100] * params.K)
    rho_alpha = np.random.dirichlet(mu_alpha, params.num_items)

    return rho_alpha

def generate_item_char_cluster(params):
    """
    Generates item characteristics using Dirichlet distributions. The realized values are
    concentrated around four randomly selected corners of the simplex.

    Parameters:
    - params (Param): An instance of the Param class.

    Returns:
    - rho_u (np.ndarray): A 2D NumPy array of shape (params.num_users, params.K) representing
      the user preferences for each category or component. The values are random 
      floats between 0 and 1, generated using Dirichlet distributions.
    """
    # Randomly select four corners
    corners = np.random.choice(params.K, size=4, replace=False)

    # Allocate space for item characteristics
    rho_alpha = np.zeros((params.num_items, params.K))

    # Concentration parameter (alpha) for Dirichlet distribution
    alpha_high = 0.01 * params.gamma_item
    alpha_low = 0.01
    alpha = [alpha_low] * params.K

    # Generate item characteristics
    for i in range(params.num_items):
        # Randomly choose one of the four corners
        corner = np.random.choice(corners)
        alpha[corner] = alpha_high  # Set the alpha parameter for the chosen corner to be high
        rho_alpha[i, :] = np.random.dirichlet(alpha)
        alpha[corner] = alpha_low  # Reset the alpha parameter for the chosen corner

    return rho_alpha



def generate_values(characteristics, preferences, params):
    """
    Generates a matrix of random values from the Beta distribution using the specified
    characteristics, preferences, and standard deviation.
    
    Parameters:
        characteristics (numpy.ndarray): A matrix of characteristics for the items.
        preferences (numpy.ndarray): A matrix of user preferences for the items.
        params (Param): An instance of the Param class.
        
    Returns:
        numpy.ndarray: A matrix of random values drawn from the Beta distribution using
        the specified characteristics, preferences, and standard deviation.
    """
    # Compute the mean preferences for each item
    mu = preferences @ characteristics.T
    
    # Set values lower than 1e-9 to 1e-9, otherwise alpha is negative
    mu = np.clip(mu, a_min=1e-9, a_max=None)
    
    # Compute the alpha and beta parameters for the Beta distribution
    alpha = ((1-mu)/(params.sigma**2) - 1/mu)*mu**2
    beta = alpha*(1/mu-1)
    
    # Generate a matrix of random values from the Beta distribution
    values = np.random.beta(alpha, beta)
    
    return values


def calculate_reserve_utilities(user_item_utility, params):
    """
    Calculate the reserve utility for each user, defined as the percentile specified by params.per of item utilities.

    Parameters:
    user_item_utility (numpy array): Matrix of user-item utilities.
    params (Param): An instance of the Param class.

    Returns:
    reserve_utilities (numpy array): Array of reserve utilities for each user.
    """
    reserve_utilities = np.percentile(user_item_utility, params.per, axis=1)

    return reserve_utilities