from functools import reduce
from itertools import combinations
from sys import argv
from time import time


def write_deliveries(outputfile, deliveries):
    with open(outputfile, 'w') as g:
        g.write(str(len(deliveries)) + '\n')
        
        for delivery in deliveries:
            g.write(' '.join(str(i) for i in delivery) + '\n')


def score_pizzas(pizzas, ids):
    return len(reduce(lambda a,b: a|b, [pizzas[id] for id in ids[1:]]))**2


def hillclimb(outputfile, deliveries, pizzas, score):
    write_deliveries(outputfile, deliveries)

    best = [deliveries, score]
    frontier = [[deliveries, score]]
    iters = [0]

    for deli, statescore in frontier:
        origscores = {x: score_pizzas(pizzas, deli[x]) for x in range(len(deli))}
        changes = []
        changed = set()

        for x1, x2 in combinations(range(len(deli)), 2):
            iters[0] += 1

            if x1 in changed or x2 in changed:
                continue

            d1 = deli[x1]
            d2 = deli[x2]

            best_improv = [0, -1, -1, -1, -1]

            for a in d1[1:]:
                for b in d2[1:]:
                    dd1 = [d for d in d1 if d != a] + [b]
                    dd2 = [d for d in d2 if d != b] + [a]
                    ds1 = score_pizzas(pizzas, dd1)
                    ds2 = score_pizzas(pizzas, dd2)                    
                    impscore = ds1+ds2-origscores[x1]-origscores[x2]
                    
                    if impscore > best_improv[0]:
                        best_improv = [impscore, x1, x2, a, b]

            if best_improv[0] > 1:
                changes.append(best_improv[1:])
                changed.add(best_improv[1])
                changed.add(best_improv[2])

        if changes:
            for x1, x2, a, b in changes:                
                deli[x1] = [deli[x1][0]] + [d for d in deli[x1][1:] if d != a] + [b]
                deli[x2] = [deli[x2][0]] + [d for d in deli[x2][1:] if d != b] + [a]

            dscore = sum(score_pizzas(pizzas, delivery) for delivery in deli)

            if dscore > best[1]:
                print(f'Hill climbed to {dscore} from {best[1]}')
                print(f'Frontier size: {len(frontier)}. Made {len(changes)} changes, from a delivery size of: {len(deliveries)} after {iters[0]} inner iterations.')                    
                best = [deli, dscore]
                frontier.append([deli, dscore])
                write_deliveries(outputfile, deli)
                        
    return best


def find_delivery(remaining, bigfirst, strat):
    MAXTRIES = 10**4

    bestdeliveries = []
    bestscore = 0
    
    for i, c in enumerate(combinations([bf for bf in bigfirst if bf[0] in remaining], sum(strat))):
        if i == MAXTRIES:
            break

        deliveries = []
        score = 0

        for s in strat:
            delivery = c[sum([len(d) for d in deliveries]):sum([len(d) for d in deliveries])+s]
            deliveries.append([d[0] for d in delivery])
            score += len(reduce(lambda a,b: a|b, [entry[1] for entry in delivery]))**2

        if score > bestscore:
            bestscore = score
            bestdeliveries = deliveries

    return bestdeliveries, bestscore


def solve(outputfile, m, t2, t3, t4, pizzas):
    deliveries = []
    bigfirst = sorted([(x, pizzas[x]) for x in range(m)], key=lambda pair: -len(pair[1]))
    remaining = {x for x in range(m)}
    score = 0
    iters = 0

    while t4 > 2 and len(remaining) > 11:
        if t4 % 100 == 0:
            print(t4, t3, t2, len(remaining), score)

        delivery = []
        ingredients = set()

        while len(delivery) < 4:
            best = [set(), -1]

            for x, pizza in bigfirst:
                if x not in remaining or x in delivery:
                    continue

                union = pizza | ingredients

                if len(union) > len(best[0]):
                    best = [union, x]

            ingredients = best[0]
            delivery.append(best[1])

        deliveries.append([4] + delivery)
        remaining -= set(delivery)
        t4 -= 1
        score += len(ingredients)**2
        bigfirst = [bf for bf in bigfirst if bf[0] in remaining]

    while t3 > 2 and len(remaining) > 8:
        if t3 % 100 < 3:
            print(t4, t3, t2, len(remaining), score)

        delivery = []
        ingredients = set()

        while len(delivery) < 3:
            best = [set(), -1]

            for x, pizza in bigfirst:
                if x not in remaining or x in delivery:
                    continue

                union = pizza | ingredients

                if len(union) > len(best[0]):
                    best = [union, x]

            ingredients = best[0]
            delivery.append(best[1])

        deliveries.append([3] + delivery)
        remaining -= set(delivery)
        t3 -= 1
        score += len(ingredients)**2

    while True:
        iters += 1

        if iters % 100 == 0:
            print(f'remaining: {len(remaining)} t4: {t4} t3: {t3} t2: {t2}')

        if t4 > 25:
            delivery, value = find_delivery(remaining, bigfirst, [4] * 20)
            score += value

            for d in delivery:
                remaining -= set(d)
                deliveries.append([len(d)] + d)

            t4 -= 20

            continue
        elif t4 == 0 and t3 > 25:
            delivery, value = find_delivery(remaining, bigfirst, [3] * 20)
            score += value

            for d in delivery:
                remaining -= set(d)
                deliveries.append([len(d)] + d)

            t3 -= 20

            continue
        elif t4 == 0 and t3 == 0 and t2 > 25:
            delivery, value = find_delivery(remaining, bigfirst, [2] * 20)
            score += value

            for d in delivery:
                remaining -= set(d)
                deliveries.append([len(d)] + d)

            t2 -= 20

            continue

        strat = [4] * min(2, t4) + [3] * min(2, t3) + [2] * min(2, t2)

        if len(strat) < 2:
            if len(strat) == 1:
                if sum(strat) <= len(remaining):
                    delivery, value = find_delivery(remaining, bigfirst, strat)
                    score += value

            return hillclimb(outputfile, deliveries, pizzas, score)

        bestdeliveries = None
        bestscore = 0
        seen = set()

        for pair in combinations(strat, 2):
            if pair in seen:
                continue

            if sum(pair) <= len(remaining):
                delivery, value = find_delivery(remaining, bigfirst, pair)

                if value > bestscore:
                    bestdeliveries = delivery
                    bestscore = value

                seen.add(pair)

        if not bestscore:
            return hillclimb(outputfile, deliveries, pizzas, score)
        
        score += bestscore

        for delivery in bestdeliveries:
            remaining -= set(delivery)
            deliveries.append([len(delivery)] + delivery)

            if len(delivery) == 4:
                t4 -= 1
            elif len(delivery) == 3:
                t3 -= 1
            else:
                t2 -= 1


def main():
    inputfiles = {
        'a': 'a_example',
        'b': 'b_little_bit_of_everything.in',
        'c': 'c_many_ingredients.in',
        'd': 'd_many_pizzas.in',
        'e': 'e_many_teams.in'
    }

    to_run = []

    if len(argv) > 2:
        print('This script only takes one optional parameter. Run either parameterless, or with one parameter, containing the letter codes for the input files you wish to process!')
        return

    if len(argv) == 2:
        if any(c not in 'abcde' for c in argv[1]):
            print('Illegal option', argv[1])
            return

        for c in set(argv[1]):
            to_run.append(inputfiles[c])

    else:
        to_run += list(inputfiles.values())

    to_run.sort()

    print('Going to run:')
    print('\n'.join(to_run))

    for file in to_run:
        t = time()
        outputfile = (file[:file.find('.')] if '.' in file else file) + '.out'
        
        with open(file) as f:
            m, t2, t3, t4 = map(int, f.readline().split())
            pizzas = []

            for _ in range(m):
                pizza = f.readline().split()
                pizzas.append(set(pizza[1:]))

            deliveries, score = solve(outputfile, m, t2, t3, t4, pizzas)

            print(f'Finished {file} with score {score} in {time()-t} seconds.')
            write_deliveries(outputfile, deliveries)

if __name__ == '__main__':
    main()