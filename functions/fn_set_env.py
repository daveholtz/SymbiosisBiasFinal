class Param:
    def __init__(self):
        self.K = Null
        self.num_periods = Null
        self.num_users =  Null
        self.num_items =  Null
        self.sigma =  Null
        self.B = Null
        self.random_seed =  Null
        self.per =  Null
        self.output_file =  Null
        
    def __init__(self, K, num_periods, num_users, num_items, sigma, B, random_seed, per, output_file):
        self.K = K
        self.num_periods = num_periods
        self.num_users = num_users
        self.num_items = num_items
        self.sigma = sigma
        self.B = B
        self.random_seed = random_seed
        self.per = per
        self.output_file = output_file

# Now, you can create an instance of this class:

