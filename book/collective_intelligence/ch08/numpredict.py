from random import random, randint
import math

def wineprice(rating, age):
    peak_age = rating - 50

    # Calculate prices based on rating
    price = rating / 2
    if age > peak_age:
        # Past its peak age, gone bad in 5 years
        price = price * (5 - (age - peak_age))
    else:
        # increase to 5x original value as it 
        # approaches its peak
        price = price * (5*((age + 1)/peak_age))

    if price < 0:
        price = 0
    return price

def wineset1():
    rows = []
    for i in range(300):
        # create a random age and rating
        rating = random()*50 + 50
        age = random()*50

        # Get reference price
        price = wineprice(rating, age)

        # Add some noise
        price *= (random()*0.4 + 0.8)

        # Add to the dataset
        rows.append({'input': (rating, age), 'result': price})

    return rows

def euclidean(v1, v2):
    d = 0.0
    for i in range(len(v1)):
        d += (v1[i] - v2[i])**2
    return math.sqrt(d)

def getdistance(data, vec1):
    distancelist = []
    for i in range(len(data)):
        vec2 = data[i]['input']
        distancelist.append((euclidean(vec1, vec2), i))
    distancelist.sort()
    return distancelist

def knnestimate(data, vec1, k = 3):
    # Get sorted distance
    dlist = getdistance(data, vec1)

    avg = 0.0

    # Take the average of the top k results
    for i in range(k):
        idx = dlist[i][1]
        avg += data[idx]['result']
    avg = avg/k

    return avg
