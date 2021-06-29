import pandas as pd
from Case import system_input


# Defines a function that returns the minimum quantity of power that can be exchanged between an offer bus and a request bus, without leading to congestions

def PTDF_check(SetPoint, Quantity, offer_bus, request_bus):
    k = 0
    m = 0
    epsilon = 0.00001  # Tolerance

    data = system_input(SetPoint)
    nodes = data['nodes']  # index for nodes
    lines = data['lines']  # index for lines
    lines_cstr = data['lines_cstr']  # index for constrained lines

    PTDF = pd.read_csv('PTDF.csv', names=nodes)  # Retrieve PTDFs from a csv file, name columns after the nodes
    PTDF['Line'] = lines  # Name rows after the lines
    PTDF.set_index('Line', inplace=True)  # Change the index to be the line names

    # Initial state
    Pl_flow = []  # List for the line flows
    Pl_max_pos = []  # List for the maximum variation of the line flows in the same direction
    Pl_max_neg = []  # List for the maximum variation of the line flows in the other direction

    for l in lines_cstr:  # Calculate power flow in each line
        Pl = 0
        for i in nodes:
            Pl += PTDF.loc[l, i] * (data[i]['SetPoint'])  # Calculate the power flow in the line by adding the contribution of each bus
        if abs(Pl) > (data[l]['lineCapacity'] + epsilon):  # Make sure that the initial power flows are feasible
            print('The initial dispatch is not feasible ({})'.format(l))
        Pl_max_pos.append(data[l]['lineCapacity'] - Pl)  # Calculate the maximum variation of the power flow in the same direction for this line
        Pl_max_neg.append(-data[l]['lineCapacity'] - Pl)  # Calculate the maximum variation of the power flow with a change of direction for this line
        Pl_flow.append(Pl)

    # Define the proper buses depending on the direction of the bids

    k = nodes[offer_bus]
    m = nodes[request_bus]

    # Update the quantity to make sure that the line flows are all feasible
    for l in lines_cstr:
        x = lines_cstr.index(l)

        PTDF_diff = - (PTDF.loc[l, k] - PTDF.loc[l, m])
        # First calculate the maximum power flow change in the line Pl_max
        if PTDF_diff > epsilon:  # If the power is flowing in the same direction
            Pl_max = max(Pl_max_pos[x], 0)
        elif PTDF_diff < -epsilon:  # If the power is flowing in the other direction
            Pl_max = min(Pl_max_neg[x], 0)
        # Then update the quantity
        if PTDF_diff > epsilon or PTDF_diff < -epsilon:  # The difference between the two PTDFs is not equal to zero
            if Pl_max / PTDF_diff < Quantity:  # If the quantity is bigger than the max for this line, update it to be equal to the max for this line
                Quantity = Pl_max / PTDF_diff
    Quantity = round(Quantity, 3)
    if Quantity == 0:
        return Quantity, 1 #returns 1 if is possible to tranfer energy
    else:
        return Quantity, 0 #returns 0 if it's not possible to tranfer energy



