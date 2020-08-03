import numpy as np

def find_best_odds(books):
    """
    Takes two-dimensional array and looks through each collumn to find the highest odd for each outcome:
    [
        [5, 7.7,  1.2],
        [4, 6.25, 1.6]
    ]

    would produce

    ([5, 7.7, 1.6],
     [0, 0,   1])
    """
    if len(books) < 2:
        raise ValueError("Must contain at least two bookers odds.")

    best = [0]*len(books[0])
    book_id = [0]*len(books[0])

    for id in range(len(books)):
        bookie = books[id]

        for i in range(len(bookie)):
            if bookie[i] > best[i]:
                best[i] = bookie[i]
                book_id[i] = id

    return (best, book_id)

def get_arbitrage(odds):
    """
    Calculate Arbitrage to find out, whether a book is worth it.
    If the arbitrage is greater than 1 you are guaranteed to loose money, if it's below 1 you are guaranteed to make money.
    """
    a = 0
    for odd in odds:
        a += 1/odd

    return a


def calculate_bets(budget, odds, arbitrage = None):
    """
    Returns bets for each outcome based on your budget and the odds
    """
    bets = []
    if arbitrage is None:
        arbitrage = get_arbitrage(odds)

    for odd in odds:
        bets.append(budget/(odd*arbitrage))

    return bets

def test_bet(bets, odds, budget):
    """
    Returns the profit for each outcome
    """

    returns = []
    for outcome in range(len(odds)):
        returns.append(bets[outcome]*odds[outcome]-budget)

    return returns
