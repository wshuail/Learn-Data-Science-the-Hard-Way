#! /usr/bin/env python2
# -*- coding: utf-8 -*-

from math import sqrt

critics={'Lisa Rose': {'Lady in the Water': 2.5, 'Snakes on a Plane': 3.5,
                       'Just My Luck': 3.0, 'Superman Returns': 3.5, 
                       'You, Me and Dupree': 2.5, 'The Night Listener': 3.0},
         'Gene Seymour': {'Lady in the Water': 3.0, 'Snakes on a Plane': 3.5,
                          'Just My Luck': 1.5, 'Superman Returns': 5.0, 
                          'The Night Listener': 3.0, 'You, Me and Dupree': 3.5},
         'Michael Phillips': {'Lady in the Water': 2.5, 'Snakes on a Plane': 3.0,
                              'Superman Returns': 3.5, 'The Night Listener': 4.0},
         'Claudia Puig': {'Snakes on a Plane': 3.5, 'Just My Luck': 3.0,
                          'The Night Listener': 4.5, 'Superman Returns': 4.0,
                          'You, Me and Dupree': 2.5},
         'Mick LaSalle': {'Lady in the Water': 3.0, 'Snakes on a Plane': 4.0,
                          'Just My Luck': 2.0, 'Superman Returns': 3.0, 
                          'The Night Listener': 3.0, 'You, Me and Dupree': 2.0},
         'Jack Matthews': {'Lady in the Water': 3.0, 'Snakes on a Plane': 4.0,
                           'The Night Listener': 3.0, 'Superman Returns': 5.0, 
                           'You, Me and Dupree': 3.5},
         'Toby': {'Snakes on a Plane':4.5, 'You, Me and Dupree':1.0,
                  'Superman Returns':4.0}}

# Return a distance-based similarity score for person1 and person2
def sim_distance(prefs, person1, person2):
    # Get the list of shared items
    si = {}
    for item in prefs[person1]:
        for item in prefs[person2]:
            si[item] = 1
    # if they have no rating in common, return 0
    if len(si) == 0:
        return 0
    
    # Add up the squares of all the differences
    sum_of_squares = sum([pow(prefs[person1][item] - prefs[person2][item], 2)
                          for item in prefs[person1] if item in prefs[person2]])
    
    return 1/(1 + sqrt(sum_of_squares))

# Return the pearson correlation score for person1 and person2
def sim_pearson(prefs, person1, person2):
    # Get the list of shared items
    si = {}
    for item in prefs[person1]:
        if item in prefs[person2]:
            si[item] = 1
    
    # print si
    
    # if they have no rating in common, return 0
    n = len(si)
    if n == 0:
        return 0
    
    # Add up the squares of all the differences
    sum1 = sum([prefs[person1][item] for item in si.keys()])
    sum2 = sum([prefs[person2][item] for item in si.keys()])
    
    # Sum up the squares
    sum1sq = sum([pow(prefs[person1][item], 2) for item in si.keys()])
    sum2sq = sum([pow(prefs[person2][item], 2) for item in si.keys()])
    
    # Sum up the products
    psum = sum([prefs[person1][item] * prefs[person2][item] for item in si.keys()])
    
    # Calculate pearson score
    num = psum - (sum1*sum2/n)
    den = sqrt((sum1sq - pow(sum1, 2)/n) * (sum2sq - pow(sum2, 2)/n))
    
    if den == 0:
        return 0
    
    r = num/den
    return r

# Returns the best matches for people from the prefs dictionay
# Number of results and similarity function are optional paras.
def top_match(prefs, person, n = 5, similarity = sim_pearson):
    score = [(similarity(prefs, person, other), other) for other in prefs if other != person]
    
    score.sort()
    score.reverse()
    
    return score[0: n]

def get_recommendation(prefs, person, similarity = sim_pearson):
    total = {}
    sim_sum = {}
    for other in prefs:
        if other == person:
            continue
        sim = similarity(prefs, person, other)
        
        if sim <= 0:
            continue
    
        for item in prefs[other]:
            if item not in prefs[person] or prefs[person][item] == 0:
                total.setdefault(item, 0)
                total[item] += prefs[other][item] * sim
                sim_sum.setdefault(item, 0)
                sim_sum[item] += sim
                
    ranking = [(total / sim_sum[item], item) for item, total in total.items()]

    ranking.sort()
    ranking.reverse()

    return ranking

def transformPrefs(prefs):
    result = {}
    for person in prefs:
        for item in prefs[person]:
            result.setdefault(item, {})

            result[item][person] = prefs[person][item]
    return result














