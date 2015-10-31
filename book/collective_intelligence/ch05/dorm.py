#! /usr/bin/env python

import random
import math

# The dorms, each has two available rooms
dorms = ['Zeus', 'Athena', 'Hercules', 'Bacchus', 'Pluto']

# People, along with their first and second choices
prefs = ['Toby', ('Bacchus', 'Hercules'),
        'Steve', ('Zeus', 'Pluto'),
        'Andrea', ('Athena', 'Zeus'),
        'Sarah', ('Zeus', 'Pluto'),
        'Dave', ('Athena', 'Bacchus'),
        'Jeff', ('Hercules', 'Pluto'),
        'Fred', ('Pluto', 'Athena'),
        'Suzie', ('Bacchus', 'Hercules'),
        'Laure', ('Bacchus', 'Hercules'),
        'Neil', ('Hercules', 'Athena')]

domain = [(0, (len(dorms)*2) -i -1) for i in range(0, len(dorms)*2)]

def printsolution(vec):
    slots = []
    # create two slots for each dorms
    for i in range(len(dorms)):
        slots += [i, i]

    # Loop over each students assignment
    for i in range(len(students)):
        x = int(vec[i])

        # choose the slot from the remaining ones
        dorm = slots[x]

        print prefs[i][0], dorm

        # remove this slot
        del slots[x]

def dormcost(vec):
    cost = 0
    slots = []
    for i in range(len(dorms)):
        slots += [i, i]

    # loop over each student
    for i in range(len(vec)):
        x = int(vec[i])
        dorm = dorms[slots[x]]
        pref = prefs[i][1]

        if dorm == pref[0]:
            cost = 0
        elif dorm == pref[1]:
            cost += 1
        else:
            cost += 3

        # remove this slot
        del slot[x]

    return cost
