import pandas as pd
from classes import Bid
from Case import system_input
import copy
import math
import random
from statistics import NormalDist
from functions import *

count_PTDF = 0
PTDF_list = []
completed_bids = []
social_welfare = 0
total_PTDF_count = 0
SetPoint = [11.416,-0.705,-0.94,-1.41,-0.94,-0.705,-1.144,-1.43,-0.286,-0.1716,-1.287,-0.47,-0.47,-0.47,-0.987] # initial set points of nodes
data = system_input(SetPoint)  # Retrieve all information of the network for this setpoint
load_gen_data = data['load_gen_data']  # list that contains all generator and load data
testcase = 4 # testcase choose from: 1:highest_social_welfare  2:largest_quantity 3:smallest_social_welfare 4:smallest_quantity
counter_network_fail = 0
counter_market_fail = 0

def market_clearing(order_book, selected_bid, data, matched_bids, read): # function to check any bid except fixed bids if they can be satisfied
    global SetPoint, social_welfare, completed_bids, total_PTDF_count, PTDF_list, testcase, counter_network_fail, counter_market_fail
    temp_list = []  # list for candidate bids that can be matched
    if selected_bid.type == "request":  # declare the bid type: request (request=true) or offer (request=false)
        request = True
    else:
        request = False

    ############ choose the bids that match with the selected bid ####################
    for bid in order_book:
        if selected_bid.type != bid.type:
            if request:
                if selected_bid.cost >= bid.cost:
                    temp_list.append(copy.deepcopy(bid))  # adding the matched bid into the list
                else:
                    counter_market_fail+=1 # counts the times that the bid couldn't be matched because of the market rules
            else:
                if selected_bid.cost <= bid.cost:
                    temp_list.append(copy.deepcopy(bid))  # adding the matched bid into the list
                else:
                    counter_market_fail+=1 # counts the times that the bid couldn't be matched because of the market rules
    ###############################################################################

    if len(temp_list) == 0:
        print("No bid in the order book matches the selected bid with id: ", selected_bid.id, "\n")
        if read:
            order_book.append(selected_bid)
        return SetPoint, order_book, data, matched_bids, 0  # return from the function with value 0 because the selected bid couldn't be matched

    total_PTDF_count, PTDF_list, final_list, temp_network = PTDF_call_function(temp_list, request, total_PTDF_count, PTDF_list, selected_bid, SetPoint)
    counter_network_fail += temp_network

    if len(final_list) == 0:
        print("Of the bids that match the selected bid with id: ", selected_bid.id, ",no bid satisfies the network constraints", "\n")
        if read:
            order_book.append(selected_bid)
        return SetPoint, order_book, data, matched_bids, 0  # return from the function with value 0 because the selected bid couldn't be matched

    fixed_final_list = []
    temp_final_list = copy.deepcopy(final_list)

    for i in final_list: # check whether the fixed bids can be satisfied, if not then remove them from the list
        if i.fixed == True:
            if i.actual_quantity != i.quantity:
                for j in temp_final_list:
                    if j.id == i.id:
                        temp_final_list.remove(j)
            elif i.quantity <= selected_bid.quantity:
                fixed_final_list.append(copy.deepcopy(i))
                for j in temp_final_list:
                    if j.id == i.id:
                        temp_final_list.remove(j)
            
    if len(fixed_final_list) != 0:
        final_list = fixed_final_list
    else:
        final_list = temp_final_list

    if len(final_list) == 0:
        print("Of the bids that match the selected bid with id: ", selected_bid.id, ",no bid satisfies the network constraints", "\n")
        if read:
            order_book.append(selected_bid)
        return SetPoint, order_book, data, matched_bids, 0  # return from the function with value 0 because the selected bid couldn't be matched

    if testcase == 1:
        temp = highest_social_welfare(final_list, selected_bid, request) # call the highest_social_welfare function in the file functions.py
    elif testcase == 2:
        temp = largest_quantity(final_list, selected_bid, request) # call the largest_quantity function in the file functions.py
    elif testcase == 3:
        temp = smallest_social_welfare(final_list, selected_bid, request) # call the smallest_social_welfare function in the file functions.py
    elif testcase == 4:
        temp = smallest_quantity(final_list, selected_bid, request) # call the smallest_quantity function in the file functions.py

    SetPoint = power_dipsatch_refresh(SetPoint, request, selected_bid, temp)    # set point refresh

    # selected bid refresh
    selected_bid, order_book, completed_bids, temp_matched_list = selected_bid_refresh(selected_bid, temp, order_book, completed_bids, read)

    temp, order_book, completed_bids = matched_bid_refresh(temp, order_book, completed_bids)  # matched bid refresh

    temp_matched_list.append(copy.deepcopy(temp))
    matched_bids.append(temp_matched_list)
    social_welfare += abs(selected_bid.cost - temp.cost) * temp.actual_quantity  # calculate the money that are excess (always the offer type bid is satisfied (always must be => offer<=request))
    return SetPoint, order_book, data, matched_bids, 1  # return from the function with value 1 because the selected bid could be matched

def fixed_bids(order_book, selected_bid, data, matched_bids, read): # function to check the fixed bids if they can be satisfied
    global SetPoint, social_welfare, completed_bids, total_PTDF_count, PTDF_list,testcase, counter_network_fail, counter_market_fail
    temp_list = []  # list for candidate bids that can be matched
    if selected_bid.type == "request":  # declare the bid type: request (request=true) or offer (request=false)
        request = True
    else:
        request = False
    ############ choose the bids that match with the selected bid ####################
    for bid in order_book:
        if selected_bid.type != bid.type and selected_bid.node != bid.node and bid.quantity >= selected_bid.quantity:
            if request:
                if selected_bid.cost >= bid.cost:
                    temp_list.append(copy.deepcopy(bid))  # adding the matched bid into the list
                else:
                    counter_market_fail+=1 # counts the times that the bid couldn't be matched because of the market rules
            else:
                if selected_bid.cost <= bid.cost:
                    temp_list.append(copy.deepcopy(bid))  # adding the matched bid into the list
                else:
                    counter_market_fail+=1 # counts the times that the bid couldn't be matched because of the market rules
    ##################################################################################

    if len(temp_list) == 0:
        print("No bid in the order book matches the selected bid with id: ", selected_bid.id, "\n")
        if read:
            order_book.append(selected_bid)
        return SetPoint, order_book, data, matched_bids, 0  # return from the function with value 0 because the selected bid couldn't be matched
  
    total_PTDF_count, PTDF_list, final_list, temp_network = PTDF_call_function(temp_list, request, total_PTDF_count, PTDF_list, selected_bid, SetPoint)
    counter_network_fail += temp_network
    if len(final_list) == 0:
        print("Of the bids that match the selected bid with id: ", selected_bid.id, ",no bid satisfies the network constraints anymore", "\n")
        if read:
            order_book.append(selected_bid)
        return SetPoint, order_book, data, matched_bids, 0  # return from the function with value 0 because the selected bid couldn't be matched

    #### checking if there are bids that can satisfy fully the fixed selected bid #####
    for i in final_list:
        if i.actual_quantity < selected_bid.quantity:
            final_list.remove(i)        

    if len(final_list) == 0:
        print("No bid in the order book satisfies the selected bid with id: ", selected_bid.id, "\n")
        if read:
            order_book.append(selected_bid)
        return SetPoint, order_book, data, matched_bids, 0  # return from the function with value 0 because the selected bid couldn't be matched
    ###################################################################################

    if testcase == 1:
        temp = highest_social_welfare(final_list, selected_bid, request) # call the highest_social_welfare function in the file functions.py
    elif testcase == 2:
        temp = largest_quantity(final_list, selected_bid, request) # call the largest_quantity function in the file functions.py
    elif testcase == 3:
        temp = smallest_social_welfare(final_list, selected_bid, request) # call the smallest_social_welfare function in the file functions.py
    elif testcase == 4:
        temp = smallest_quantity(final_list, selected_bid, request) # call the smallest_quantity function in the file functions.py

    SetPoint = power_dipsatch_refresh(SetPoint, request, selected_bid, temp)  # set point refresh

    # selected bid refresh
    selected_bid, order_book, completed_bids, temp_matched_list = selected_bid_refresh(selected_bid, temp, order_book, completed_bids, read)

    temp, order_book, completed_bids = matched_bid_refresh(temp, order_book, completed_bids)  # matched bid refresh

    temp_matched_list.append(copy.deepcopy(temp))
    matched_bids.append(temp_matched_list)
    social_welfare += abs(selected_bid.cost - temp.cost) * temp.actual_quantity  # calculate the money that are excess (always the offer type bid is satisfied (always must be => offer<=request))
    return SetPoint, order_book, data, matched_bids, 1 # return from the function with value 1 because the selected bid could be matched

def input_data(time):   # declaring power percentage of each load and gen type for the specific hour 
    global power_PV, power_WT, power_H, power_F
    csv_input_data = pd.read_csv('input data.csv')
    for index, row in csv_input_data.iterrows():
        if row['TIME'] == time:
            power_PV = row['POWER P/V(MW)']
            power_WT = row['POWER W/T(MW)']
            power_H = row['POWER_H(MW)']
            power_F = row['POWER_F(MW)']
            break

def calculate_bid(list):
    k = 1 # id counter
    big_list = []
    counter = 0
    for i in list:
        normal_dist = 0
        counter = counter + 1
        temp_list = []
        if i[1] == 0:
            continue
        if i[2] == 'wt':        # declaring the generator power if wt:wind turbine
            estimated_power_factor = power_WT
        elif i[2] == 'pv':      # declaring the generator power if pv:photovoltaic
            estimated_power_factor = power_PV
        elif i[2] == 'hb':   # declaring the load power if hb: household bus
            estimated_power_factor = power_H
        elif i[2] == 'fb':      # declaring the load power if fb: factory bus
            estimated_power_factor = power_F
        estimated_power = estimated_power_factor*i[1]  # the estimated power is equal to the product of the nomimal power times(x) the power factor 
        sigma = random.randint(1, 20)/100 # deviation equal to the range of 0.01 to 0.20
        x = random.randint(1, 2)
        if x == 1: # the real power will be smaller than the estimated power
            normal_dist = NormalDist(mu=estimated_power_factor, sigma=sigma).inv_cdf(0.5-i[3]/2)
            normal_dist_power = normal_dist*estimated_power
        else:    # the real power will be greater than the estimated power
            normal_dist = NormalDist(mu=estimated_power_factor, sigma=sigma).inv_cdf(1-i[3]/2)
            if normal_dist > 1:
                normal_dist_power = normal_dist * estimated_power
            else:
                normal_dist_power = (2-normal_dist)*estimated_power
            if normal_dist_power > i[1]:
                normal_dist_power = i[1]
        power = normal_dist_power-estimated_power # the power of the bid is the difference between real power and estimated power 

        if power > 0:   # if the power is positive the bid type is offer 
            type = "offer"
            random_price = random.randint(400, 550)  # price = random number between 400 - 550 
        else:
            type = "request"    # if the power is negative the bid type is request 
            random_price = random.randint(500, 650)  # price = random number between 500 - 650 
           
        temp_list = [k, type, random_price/10, round(abs(power), 2), round(abs(power), 2), 0, i[0], 'FALSE', 'FALSE']
        big_list.append(temp_list)
        
        if True: # comfort bids creation 
            new_k = 'F' + str(k)
            temp_list_2 = []
            r = random.randint(10, 20)/100  # random number between 0.10 - 0.20 that represents the variation of the power
            random_number = random.randint(1, 2) # 1: the power decreases, 2: the power increases 
            if (i[2] == 'hb' or i[2] == ' fb') and random_number == 1: # for generator type the power only decreases 
                new_price = random.randint(random_price-50, random_price-20)/10 #
                new_power = r * normal_dist_power
                temp_list_2 = [new_k, 'request', new_price, round(abs(new_power), 2), round(abs(new_power), 2), 0, i[0], 'FALSE', 'FALSE']   
            else: # for load type the power increases and decreases 
                new_price = random.randint(random_price+20, random_price+50)/10 
                new_power = r * normal_dist_power
                if new_power < (0.05*i[1]):
                    new_power = 0.05*i[1]
                temp_list_2 = [new_k, 'offer', new_price, round(abs(new_power), 2), round(abs(new_power), 2), 0, i[0], 'FALSE', 'FALSE']   
            big_list.append(temp_list_2)         

        k += 1
    random.shuffle(big_list)   # randomizes the bid order
    df = pd.DataFrame(big_list, columns=['id', 'type', 'cost', 'initial quantity', 'quantity', 'actual quantity', 'node', 'completely matched', 'fixed'])
    df.to_csv('bids.csv', index=False)
    print('Total generators and loads checked = ', counter, '\n')

csv_file = pd.read_csv("bids.csv")
time = 13    # declaration of the running time of the market
print("The current time is: ", time, "\n")
matched_bids = []
order_book = []
fixed_bids_list = []

input_data(time) #call the input_data function of the current time
create_bids = False  # if true new bids are created 
if create_bids:
    calculate_bid(load_gen_data)

for index, row in csv_file.iterrows():     # reading of all bids and market check
    new_bid = Bid(row['id'], row['type'].lower(), float(row['cost']), float(row['initial quantity']), float(row['quantity']), float(row['actual quantity']), row['node'], row['completely matched'], row['fixed'])
    if new_bid.fixed == True:
        SetPoint, order_book, data, matched_bids, is_matched = fixed_bids(order_book, new_bid, data, matched_bids, True)
    else:
        SetPoint, order_book, data, matched_bids, is_matched = market_clearing(order_book, new_bid, data, matched_bids, True)

print("The reading of the bids has been performed and now the remaining bids in the order book will be checked", "\n", "\n", "\n", "\n")

############ check after all the bids have been read ##################
k = 1
final_bids = copy.deepcopy(order_book)
while k:
    k = 0
    for bid in order_book:
        for i in final_bids:
            if i.id == bid.id:
                if i.fixed == True:
                    SetPoint, final_bids, data, matched_bids, is_matched = fixed_bids(final_bids, i, data, matched_bids, False)
                else:
                    SetPoint, final_bids, data, matched_bids, is_matched = market_clearing(final_bids, i, data, matched_bids, False)
                if is_matched:
                    k = 1
#######################################################################3

if len(final_bids) == 0:
   print("All bids have been matched", "\n", "\n")
else:
   print("No more bids can be matched", "\n", "\n")

print("The social welfare is: ", social_welfare, "\n", "\n")
print("The list of matched bids is: ", "\n")
print_matched_bid_list(matched_bids) # print the list of matched bids
print("\n", "\n")

# extract the list of matched bids to csv
final_matched_list = create_matched_list_from_bids(matched_bids)
df = pd.DataFrame(final_matched_list, columns=['Selected ID', 'type', 'cost', 'initial quantity', 'quantity', 'node', 'completely matched', 'Matched ID', 'type', 'cost', 'initial quantity', 'quantity', 'ACTUAL QUANTITY TRANSFERRED', 'node', 'completely matched', 'social welfare'])
df.to_csv('matched bids.csv', index=False)

if len(final_bids) == 0:
    print("The final order book is empty ", "\n")
else:
    print("The final order book is: ", "\n")
print_bid_list(final_bids)  # print the final order book
print("\n", "\n")

# extract the list of the final order book to csv
df = pd.DataFrame(create_list_from_order_book(final_bids), columns=['ID', 'type', 'cost', 'initial quantity', 'quantity', 'node', 'completely matched'])
df.to_csv('order book.csv', index=False)

print("The following shows the node and the PTDF checks performed for each bid that was checked through PTDF at least once:", "\n")
for bid in PTDF_list:       # print PTDF_list
    print("The bid id is:", bid.id, " and the PTDF count is:", bid.counter)
print("\n", "\n")

node_set_points = []
for i,j in enumerate(SetPoint):
    node_set_points.append([i+1, j])
df = pd.DataFrame(node_set_points, columns=['Node', 'Set Point'])
df.to_csv('set points.csv', index=False)     #extract the list of set points

df = pd.DataFrame(create_list_from_completed_bids(completed_bids), columns=['ID', 'type', 'cost', 'initial quantity', 'node', 'completely matched'])
df.to_csv('completed bids.csv', index=False)   #extract completed bids list

PTDF_csv_list = []
for bid in PTDF_list:
    temp = []
    temp.append(bid.id)
    temp.append(bid.counter)
    PTDF_csv_list.append(temp)
PTDF_csv_list.append(['total PTDF count', total_PTDF_count])

temp_network = ['network counter', counter_network_fail]
temp_market = ['market counter', counter_market_fail]
PTDF_csv_list.append(temp_network)
PTDF_csv_list.append(temp_market)

df = pd.DataFrame(PTDF_csv_list, columns=['id', 'PTDF_count'])
df.to_csv('PTDF_count.csv', index=False)       # extract the PTDF list to csv

k = 1
print("The present power at each node is:", "\n")
for node in SetPoint:
    print("The power at the node", k, " is equal to", "{:.3f}".format(node))   # print SetPoint of each node
    k += 1
print("\n", "\n")

data = system_input(SetPoint)
for key in data:
    print(key, ' : ', data[key])    # print data of network
print("\n")

df = pd.DataFrame.from_dict(data, orient="index")
df.to_csv("data.csv")   # extract data of network to csv