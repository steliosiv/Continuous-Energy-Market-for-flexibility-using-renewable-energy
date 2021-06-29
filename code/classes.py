class Bid: # class of a bid object 

    def __init__(self, id, bid_type, cost, initial_quantity, quantity, actual_quantity, node, completely_matched, fixed):
        self.id = id
        self.type = bid_type
        self.cost = cost
        self.initial_quantity = initial_quantity
        self.quantity = quantity
        self.actual_quantity = actual_quantity
        self.node = node
        self.completely_matched = completely_matched
        self.fixed = fixed

class Counter:

    def __init__(self, id, count):
        self.id = id
        self.counter = count