import copy
from operator import add
from PTDF import PTDF_check
from classes import Counter
from classes import Bid

def print_bid_list(list):
    for bid in list:
        print("The bid id is:", bid.id, " the type is:", bid.type)

def print_matched_bid_list(list):
    for match in list:
        print("The selected bid id is:", match[0].id, " the type is:", match[0].type, "the matched bid id is:", match[1].id, " with transfered quantity of: ", match[1].actual_quantity, "\n")

def create_list_from_order_book(list):
    temp = []
    for bid in list:
        temp2 = []
        temp2.append(bid.id)
        temp2.append(bid.type)
        temp2.append(bid.cost)
        temp2.append(bid.initial_quantity)
        temp2.append(bid.quantity)
        temp2.append(bid.node)
        temp2.append(bid.completely_matched)
        temp.append(temp2)
    return temp

def create_list_from_completed_bids(list):
    temp = []
    for bid in list:
        temp2 = []
        temp2.append(bid.id)
        temp2.append(bid.type)
        temp2.append(bid.cost)
        temp2.append(bid.initial_quantity)
        temp2.append(bid.node)
        temp2.append(bid.completely_matched)
        temp.append(temp2)
    return temp

def create_matched_list_from_bids(list):
    temp = []
    for match in list:
        temp1 = []
        temp1.append(match[0].id)
        temp1.append(match[0].type)
        temp1.append(match[0].cost)
        temp1.append(match[0].initial_quantity)
        temp1.append(match[0].quantity)
        temp1.append(match[0].node)
        temp1.append(match[0].completely_matched)
        temp2 = []
        temp2.append(match[1].id)
        temp2.append(match[1].type)
        temp2.append(match[1].cost)
        temp2.append(match[1].initial_quantity)
        temp2.append(match[1].quantity)
        temp2.append(match[1].actual_quantity)
        temp2.append(match[1].node)
        temp2.append(match[1].completely_matched)
        sw = abs(match[0].cost - match[1].cost) * match[1].actual_quantity
        temp2.append(sw)
        temp.append(temp1+temp2)
    return temp

def matched_bid_refresh(temp, order_book, completed_bids):
    if temp.quantity - temp.actual_quantity > 0.0001:  # if the matched bid has remaining power then it return to the order book with the remaining power 
        for i in order_book:
            if temp.id == i.id:
                change_bid = copy.deepcopy(i)
                change_bid.quantity = temp.quantity - temp.actual_quantity
                change_bid.completely_matched = False
                order_book.remove(i)
                order_book.append(change_bid)
                break
    else:
        for i in order_book:
            if temp.id == i.id:
                temp.quantity = temp.quantity - temp.actual_quantity
                temp.completely_matched = True
                order_book.remove(i)
                completed_bids.append(temp)
                break
    return temp, order_book, completed_bids

def selected_bid_refresh(selected_bid, temp, order_book, completed_bids, read):

    temp_matched_list = []
    if selected_bid.quantity - temp.actual_quantity > 0.0001:  # if the selected bid is not fully satisfied then it return to the order book with the remaining power that needs
        temp_matched_list.append(copy.deepcopy(selected_bid))
        if read:  # if true then the bid will be checked for the first time 
            selected_bid.quantity = selected_bid.quantity - temp.actual_quantity
        else:  # else it is already in the order book
            for i in order_book:
                if i.id == selected_bid.id:
                    order_book.remove(i)
                    break
            selected_bid.quantity = selected_bid.quantity - temp.actual_quantity
        selected_bid.completely_matched = False
        order_book.append(selected_bid)

    else:  # else the selected bid is fully satisfied
        selected_bid.quantity = selected_bid.quantity - temp.actual_quantity
        selected_bid.completely_matched = True
        temp_matched_list.append(copy.deepcopy(selected_bid))
        completed_bids.append(copy.deepcopy(selected_bid))
        if not (read):  # if true, it is in the order book and must be removed
            for i in order_book:
                if i.id == selected_bid.id:
                    order_book.remove(i)
                    break
    return selected_bid, order_book, completed_bids, temp_matched_list

def PTDF_call_function(temp_list, request, total_PTDF_count, PTDF_list, selected_bid, SetPoint):
    count_PTDF = 0
    final_list = []  # the final candidate list of bids that can satisfy the selected bid considering the network constraints
    for bid_item in temp_list:
        quantity = min(bid_item.quantity, selected_bid.quantity)
        quantity = round(quantity, 5)
        if request:
            result,temp = PTDF_check(SetPoint, quantity, bid_item.node - 1, selected_bid.node - 1)
            count_PTDF += 1
            total_PTDF_count += 1
        else:
            result,temp = PTDF_check(SetPoint, quantity, selected_bid.node - 1, bid_item.node - 1)
            count_PTDF += 1
            total_PTDF_count += 1
        if result > 0:
            bid_item.actual_quantity = min(quantity, result)
            final_list.append(copy.deepcopy(bid_item))
    PTDF = Counter(selected_bid.id, count_PTDF)
    PTDF_list.append(PTDF)

    return total_PTDF_count, PTDF_list, final_list, temp

def power_dipsatch_refresh(SetPoint, request, selected_bid, temp):
    ###### set point refresh of the two nodes with the transfer quantity ########

    Delta = [0] * len(SetPoint)
    if request:
        Delta[selected_bid.node - 1] += temp.actual_quantity
        Delta[temp.node - 1] -= temp.actual_quantity
    else:
        Delta[selected_bid.node - 1] -= temp.actual_quantity
        Delta[temp.node - 1] += temp.actual_quantity
    SetPoint = list(map(add, SetPoint, Delta))  # modify the setpoint and update the status marker
    temp_SetPoint = copy.deepcopy(SetPoint)
    SetPoint = []
    for i in temp_SetPoint:
        temp_value = round(i, 5)
        SetPoint.append(temp_value)
    return SetPoint

def highest_social_welfare(final_list, selected_bid, request):
    temp = final_list.pop(0)
    if request:  # selected_bid of type request
        for bid in final_list:  # bid in final_list of type offer
            if temp.cost > bid.cost or (temp.cost == bid.cost and temp.actual_quantity < bid.actual_quantity):  # choose the correct bid firstly based on cost and then on quantity 
                temp = bid
        print("The bid with id: ", selected_bid.id, " is matched with the bid with id: ", temp.id, " ,Request bus node: ", selected_bid.node, " .Offer bus node is: ", temp.node,  " . The power that is transfered is: ", temp.actual_quantity, "\n")
    if not(request):  # selected_bid of type offer
        for bid in final_list:  # bid in final_list of type request
            if temp.cost < bid.cost or (temp.cost == bid.cost and temp.actual_quantity < bid.actual_quantity):  # choose the correct bid firstly based on cost and then on quantity 
                temp = bid
        print("The bid with id: ", selected_bid.id, " is matched with the bid with id: ", temp.id, " .Offer bus node is: ", selected_bid.node, " ,request bus node: ", temp.node, " . The power that is transfered is: ", temp.actual_quantity, "\n")
    return temp

def largest_quantity(final_list, selected_bid, request):
    temp = final_list.pop(0)
    for bid in final_list:  # bid in final_request list of type offer
        if temp.actual_quantity < bid.actual_quantity:  # choose the correct bid based on the quantity 
                temp = bid
    if request:  # selected_bid tipou request
        print("The bid with id: ", selected_bid.id, " is matched with the bid with id: ", temp.id, " ,Request bus node: ", selected_bid.node, " .Offer bus node is: ", temp.node, " . The power that is transfered is: ", temp.actual_quantity, "\n")
    else:
        print("The bid with id: ", selected_bid.id, " is matched with the bid with id: ", temp.id, " .Offer bus node is: ", selected_bid.node, " ,request bus node: ", temp.node, " . The power that is transfered is: ", temp.actual_quantity, "\n")
    return temp

def smallest_social_welfare(final_list, selected_bid, request):
    temp = final_list.pop(0)
    if request:  # selected_bid of type request
        for bid in final_list:  # bid in final_list of type offer
            if temp.cost < bid.cost or (temp.cost == bid.cost and temp.actual_quantity < bid.actual_quantity):  # choose the correct bid firstly based on cost and then on quantity 
                temp = bid
        print("The bid with id: ", selected_bid.id, " is matched with the bid with id: ", temp.id, " ,Request bus node: ", selected_bid.node, " .Offer bus node is: ", temp.node,  " . The power that is transfered is: ", temp.actual_quantity, "\n")
    if not(request):  # selected_bid of type offer
        for bid in final_list:  # bid in final_list of type request
            if temp.cost > bid.cost or (temp.cost == bid.cost and temp.actual_quantity < bid.actual_quantity):  # choose the correct bid firstly based on cost and then on quantity 
                temp = bid
        print("The bid with id: ", selected_bid.id, " is matched with the bid with id: ", temp.id, " .Offer bus node is: ", selected_bid.node, " ,request bus node: ", temp.node, " . The power that is transfered is: ", temp.actual_quantity, "\n")
    return temp

def smallest_quantity(final_list, selected_bid, request):
    temp = final_list.pop(0)
    for bid in final_list:  # bid in final_request list of type offer
        if temp.actual_quantity > bid.actual_quantity:  # choose the correct bid based on the quantity 
                temp = bid
    if request:  # selected_bid of type request
        print("The bid with id: ", selected_bid.id, " is matched with the bid with id: ", temp.id, " ,Request bus node: ", selected_bid.node, " .Offer bus node is: ", temp.node, " . The power that is transfered is: ", temp.actual_quantity, "\n")
    else:
        print("The bid with id: ", selected_bid.id, " is matched with the bid with id: ", temp.id, " .Offer bus node is: ", selected_bid.node, " ,request bus node: ", temp.node, " . The power that is transfered is: ", temp.actual_quantity, "\n")
    return temp

