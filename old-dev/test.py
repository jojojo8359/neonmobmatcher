from numpy.random import choice


def rarityOdds(rarityRatio, compact=False):
    MIN_RATIO = 0.5
    oddsText = 'most' if compact else 'almost all'
    if rarityRatio <= MIN_RATIO:
        oddsText = '' if compact else '1 in '
        oddsText += str(round(1 / rarityRatio))
    return oddsText


def freebieRarityOdds(total_prints, total_print_count, prints_per_free_pack):
    rarityRatio = total_prints / total_print_count * prints_per_free_pack
    return rarityOdds(rarityRatio)


def roll(common, uncommon, rare, v_rare, e_rare, chase, variant, legendary, cards):
    rarities = [0, 0, 0, 0, 0, 0, 0, 0]
    for index, rarity in enumerate([common, uncommon, rare, v_rare, e_rare, chase, variant, legendary]):
        if rarity != 'all' and rarity != 0:
            rarities[index] = rarity / cards
        elif rarity == 'all':
            rarities[index] = 'all'
    alls = rarities.count('all')
    rarity_sum = float(0)
    for rarity in rarities:
        if isinstance(rarity, float):
            rarity_sum += rarity
    for index, rarity in enumerate([common, uncommon, rare, v_rare, e_rare, chase, variant, legendary]):
        if rarity == 'all':
            rarities[index] = (1 - rarity_sum) / alls
    print("Common: " + str(rarities[0]))
    print("Uncommon: " + str(rarities[1]))
    print("Rare: " + str(rarities[2]))
    print("Very Rare: " + str(rarities[3]))
    print("Extra Rare: " + str(rarities[4]))
    print("Chase: " + str(rarities[5]))
    print("Variant: " + str(rarities[6]))
    print("Legendary: " + str(rarities[7]))
    return choice(range(8), 553 * 2, p=rarities)


# print(freebieRarityOdds(395624, 1165294, 2))

# Common: 11636 x34 = 395624
# Uncommon: 7250 x34 = 246500
# Rare: 4995 x34 = 169830
# Very Rare: 3740 x34 = 127160
# Extra Rare: 3730 x34 = 126820
# Chase: 2760 x36 = 99360

# Total: 1165294

# print(roll('all', 1/2, 1/3, 1/5, 1/12, 1/19, 0, 2))
results = list(roll('all', 1/2, 1/3, 1/5, 1/13, 1/20, 1/15, 1/553, 2))
# print(results)
print(results.count(7))
