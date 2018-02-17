"""

Usage:
    $python apriori.py -f DATASET.csv -s minSupport  -c minConfidence

    $python apriori.py -f DATASET.csv -s 0.15 -c 0.6
"""

import sys

from itertools import chain, combinations
from collections import defaultdict
from optparse import OptionParser
import random

def subsets(arr):
    """ Returns non empty subsets of arr"""
    return chain(*[combinations(arr, i + 1) for i, a in enumerate(arr)])


def returnItemsWithMinSupport(itemSet, transactionList, minSupport, freqSet):
        """calculates the support for items in the itemSet and returns a subset
       of the itemSet each of whose elements satisfies the minimum support"""
        _itemSet = set()
        localSet = defaultdict(int)

        for item in itemSet:
                for transaction in transactionList:
                        if item.issubset(transaction):
                                freqSet[item] += 1
                                localSet[item] += 1

        for item, count in localSet.items():
                support = float(count)/len(transactionList)

                if support >= minSupport:
                        _itemSet.add(item)

        return _itemSet


def joinSet(itemSet, length):
        """Join a set with itself and returns the n-element itemsets"""
        return set([i.union(j) for i in itemSet for j in itemSet if len(i.union(j)) == length])


def getItemSetTransactionList(data_iterator):
    transactionList = list()
    itemSet = set()
    for record in data_iterator:
        transaction = frozenset(record)
        transactionList.append(transaction)
        for item in transaction:
            itemSet.add(frozenset([item]))              # Generate 1-itemSets
    return itemSet, transactionList


def runApriori(data_iter, minSupport, minConfidence):
    """
    run the apriori algorithm.
    Return both:
     - items (tuple, support)
     - rules ((pretuple, posttuple), confidence)
    """
    itemSet, transactionList = getItemSetTransactionList(data_iter)

    freqSet = defaultdict(int)
    largeSet = dict()
    # Global dictionary which stores (key=n-itemSets,value=support)
    # which satisfy minSupport

    assocRules = dict()
    # Dictionary which stores Association Rules

    oneCSet = returnItemsWithMinSupport(itemSet,
                                        transactionList,
                                        minSupport,
                                        freqSet)

    currentLSet = oneCSet
    k = 2
    while(currentLSet != set([])):
        largeSet[k-1] = currentLSet
        currentLSet = joinSet(currentLSet, k)
        currentCSet = returnItemsWithMinSupport(currentLSet,
                                                transactionList,
                                                minSupport,
                                                freqSet)
        currentLSet = currentCSet
        k = k + 1

    def getSupport(item):
            """local function which Returns the support of an item"""
            return float(freqSet[item])/len(transactionList)

    toRetItems = []
    for key, value in largeSet.items():
        toRetItems.extend([(tuple(item), getSupport(item))
                           for item in value])

    toRetRules = []
    for key, value in largeSet.items()[1:]:
        for item in value:
            _subsets = map(frozenset, [x for x in subsets(item)])
            for element in _subsets:
                remain = item.difference(element)
                if len(remain) > 0:
                    confidence = getSupport(item)/getSupport(element)
                    if confidence >= minConfidence:
                        toRetRules.append(((tuple(element), tuple(remain)),
                                           confidence))
    return toRetItems, toRetRules


def printResults(items, rules):
    """prints the generated itemsets sorted by support and the confidence rules sorted by confidence"""
    for item, support in sorted(items, key=lambda (item, support): support):
         print "item: %s , %.3f" % (str(item), support)
    print "\n------------------------ RULES ------------------------"
    for rule, confidence in sorted(rules, key=lambda (rule, confidence): confidence):
        pre, post = rule
        print "Rule: %s ==> %s , %.3f" % (str(pre), str(post), confidence)


def dataFromFile(fname):
        """Function which reads from the file and yields a generator"""
        file_iter = open(fname, 'rU')
        for line in file_iter:
                line = line.strip().rstrip(',')                         # Remove trailing comma
                record = frozenset(line.split(','))
                yield record


def start(tags):

    # optparser = OptionParser()
    # optparser.add_option('-f', '--inputFile',
    #                      dest='input',
    #                      help='filename containing csv',
    #                      default=None)
    # optparser.add_option('-s', '--minSupport',
    #                      dest='minS',
    #                      help='minimum support value',
    #                      default=0.15,
    #                      type='float')
    # optparser.add_option('-c', '--minConfidence',
    #                      dest='minC',
    #                      help='minimum confidence value',
    #                      default=0.6,
    #                      type='float')

    # (options, args) = optparser.parse_args()

    # inFile = dataFromFile('dresses.csv');
    # minSupport = 0.1
    # minConfidence = 0.1


    inFile = dataFromFile('INTEGRATED-DATASET.csv');
    minSupport = 0.17  # options.minS
    minConfidence = 0.68  # options.minC

    items, rules = runApriori(inFile, minSupport, minConfidence)

    # print "\n------------------------ RULES:"
    # for rule, confidence in sorted(rules, key=lambda (rule, confidence): confidence):
    #     pre, post = rule
    #     print "Rule: %s ==> %s , %.3f" % (str(pre), str(post), confidence)

    # printResults(items, rules)

    # could use an randomize
    #rule = random.shuffle(rules)

    max_confidence = 0;
    temp = None;

    for rule, confidence in sorted(rules, key=lambda (rule, confidence): confidence):
        pre, post = rule

        # if len(pre)==len(tags) and len(post)==1 and set(pre).issubset(set(tags)) and set(tags).issubset(set(pre)):
        # if len(post) == 1 and set(tags).issubset(set(pre)):

        if set(tags).issubset(set(pre)) and max_confidence<confidence:
            print "Rule: %s ==> %s , %.3f" % (str(pre), str(post), confidence)
            temp = post;

    return temp;



# yoyo = ['female', 'Bodycon_Dresses', 'USA', 'Cocktail_Dresses'];
# print "result = " + str(start(yoyo))
