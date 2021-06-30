# Continuous Energy Market for flexibility using renewable energy
This project was made in python and was created for my thesis in my final year as an electrical engineer student. The purpose of this code is to run a continuous market to provide flexibility to the users while it respects the network constraints (the network is checked with the PTDF coefficients)

## Code

The inspiration for the code was the article (Prat, Eléa & Herre, Lars & Kazempour, Jalal & Chatzivasileiadis, Spyros. (2020). “Design of a Continuous Local Flexibility Market with Network Constraints.”) whose code can be found [here](https://github.com/eleaprat/LFM--Online-Appendix).

The files case.py and PTDF.py have been slightly changed  in order for our code to work. The main code was built entirely from the scratch in my own unique way. The main code which is responsible for running the market is in the file Stelios_main.py. The file functions.py contains all the functions that are used in the main program and the file classes.py contains the two types of classes that are used.

I created two types of bids not comfort bids and comfort bids. Not comfort bids are based on the differnce between the estimated power and real power. As for the comfort bids, those are calculated using a 10-20 variation in the load and generators. For the creation of both bid types the normal distribution is used.

The main code gets its data from the files that are extracted from matpower for a case. Those files are:
baseMVA.csv: contains the power base in MVA
branch.csv: contains all the information regarding the lines of the network
bus.csv: contains all the inormation about each bus of the network
gen.csv: contains information about each generator of the network
gencost.csv: contains infortmation about the cost of each generator

The bids of the market are created using the normal distribution and the data of real time energy found in the file input data.csv
bids.csv: contains all the bids that are about to be entered in the market
The file PTDF.csv contains all the PTDF of the network

The results of each run are exctracted in csv files:
* completed bids.csv: contains all the information regarding the completed bids of the market
* data.csv: contains all the information regarding the network after the market has run
* matched bids.csv: contains all the information about the pair of bids that were matched
* order book: contains the information about the remaining bids that couldn't be matched
* PTDF_count: contains the number of times the PTDF function was called for each bid
* set points: contains the final power value of each node after the market has run

I included four types of methods in order to select a bid of those who satissfy the market rules and network constraints, those types are:
* highest social welfare: returns the bid that has the biggest difference in price
* lowest social welfare: returns the bid that has the smallest difference in price
* highest quantity: returns the bid with the highest quantity
* lowest quantity: returns the bid with the lowest quantity

## Power data.xlsx
We ran the market for 6 different hours in a day. Those 6 different hours represent states at which the network may face challenges, To find these 6 hours we calcualted the load, production and net load of each hour based on real time data of consumption and renewable energy production. 

The six hours that are tested are:

* 3: min load
* 4: min net load
* 12: max load
* 13: max production
* 19: max net load
* 21: min production

Also, in this file are the calculations for the power at each node

## RESULTS

The rusults of the simulation can be found in the two folders (not comfort bids) and (comfort bids). Each folder contains the results of each of the six hours, and for each hour the results of the four selecting methods.

A summary of the results and some interesting statistics can be found in the file RESULTS.xlsx

### Further explanation
For further explanation of the code, you can read my thesis which will be found in the link that will be posted in the coming days


