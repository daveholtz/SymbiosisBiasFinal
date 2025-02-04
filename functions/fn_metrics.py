def avg_take_up_rate_by_period(prev_consumed_items, user_assignments,params):
    """
    Calculate the average take-up rate for two different algorithms in each period.

    Parameters:
    consumption_history (list): List of item IDs corresponding to each user's consumption history after the initial period.
    user_assignments (list): List of user assignments to one of the two algorithms (0 or 1).

    Returns:
    algo_1_avg (list): List of average consumption rates for Algorithm 1 by period.
    algo_2_avg (list): List of average consumption rates for Algorithm 2 by period.
    """

    num_periods = len(prev_consumed_items[0])
    algo_1_sum = [0] * num_periods
    algo_2_sum = [0] * num_periods

    # Calculate the count for each algorithm once
    algo_1_count = sum(1 for assignment in user_assignments if assignment == 0)
    algo_2_count = sum(1 for assignment in user_assignments if assignment == 1)

    # Iterate through users and their consumption history
    for user_id, consumption_history in enumerate(prev_consumed_items):
        for period, consumption in enumerate(consumption_history):
            # If user is assigned to Algorithm 1 and consumption is not -1 (-1 means the user did not consume anything) and not > num_items_per_period * period (only item IDs up to num_items_per_period * period should be introduced), increment the sum for Algorithm 1
            if user_assignments[user_id] == 0 and consumption != -1 and consumption <=  params.num_items_per_period * period-1:
                algo_1_sum[period] += 1
            # If user is assigned to Algorithm 2 and consumption is not -1 and not > num_items_per_period * period, increment the sum for Algorithm 2
            elif user_assignments[user_id] == 1 and consumption != -1 and consumption <= params.num_items_per_period * period-1:
                algo_2_sum[period] += 1

    # Calculate the average consumption rate for each period for both algorithms
    algo_1_avg = [s / algo_1_count for s in algo_1_sum]
    algo_2_avg = [s / algo_2_count for s in algo_2_sum]

    return algo_1_avg, algo_2_avg