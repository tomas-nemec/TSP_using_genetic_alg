import random
import math

class City:     # gen
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def euklid_distance(self, city):    # funkcia pre pocitanie vzdialenosti medzi 2 mestami
        d_x = abs(self.x - city.x)
        d_y = abs(self.y - city.y)
        d_total = math.sqrt(d_x**2 + d_y**2)
        return d_total

    # pomocna funkcia vypis
    def introduce(self):
        what = str(self.x) + "," + str(self.y)
        return what

class Route:    # chromozom/indivuduo
    def __init__(self, path):
        self.path = path    # list objektov City
        self.value_path = 0 # hodnota fitness (vzdialenost ktoru prejdeme ked pojdeme po ceste)

    def route_fitness(self):   # fitness funkcia, vypocita celkovu hodnotu cesty
        total_distance = 0
        for i in range(0, len(self.path), 1):
            if(i != len(self.path) - 1):
                total_distance += self.path[i].euklid_distance(self.path[i + 1])
            else:
                total_distance += self.path[i].euklid_distance(self.path[0])
        self.value_path = round(total_distance,2)

    # pomocna funkcia vypis
    def write_path(self):
        for i in self.path:
            print(i.introduce())

"""     TRIEDY ZADEFINOVANE     """
def create_city(maxXY): # vytvori mesto s nahodnymi udajmi X,Y
    city = City(random.randint(0,maxXY), random.randint(0,maxXY))
    return city

def create_cities(num_cities, max_xy):  # nahodne vytvori mesta
    citiess = []
    for i in range(0, num_cities, 1):
        citiess.append(create_city(max_xy))
    return citiess

def create_route(cities): # nahodne vytvori cesty z miest
    example = cities.copy()
    new_route = []
    for i in range(0, len(example)):
        a = random.choice(example)
        example.remove(a)
        new_route.append(a)
    return new_route

def create_population(size_of_population, cities):  # funkcia na vytvorenie pociatocnej populacie
    population = []
    for i in range(0,size_of_population): # podla velkosti populacie vytvorim x nahodnych ciest a pridam ich do populacie
        route = Route(create_route(cities))
        population.append(route)

    population = fitness(population)   # ked mam uz populaciu, ohodnotim ju
    return population

def fitness(population):    # zavolam nad kazdym individuom(chromozomom) funkciu route_fitness co vypocita jeho fitness hodnotu
    for i in population:
        i.route_fitness()
    sorted_population = sorted(population, key=lambda path: path.value_path)    # zoradim od najlepsej po najhorsiu
    return sorted_population

"""     SPOSOBY SELEKCIE        """
def tournament(act_pop, subSize):  # selekcia TURNAJ
    pop1 = act_pop.copy()
    length_pop1 = len(pop1) - 1
    competitors = []
    for i in range(0, subSize, 1):  # nahodne vyberem X individuii z populacie
        a = pop1[random.randint(0, length_pop1)]
        length_pop1 -= 1
        pop1.remove(a)
        competitors.append(a)


    lowest = competitors[0].value_path
    winner = competitors[0]
    for i in competitors:   # vyberiem z COMPETITORS najlepsieho
        if (i.value_path < lowest):
            lowest = i.value_path
            winner = i

    return winner

def rulette(act_pop):   # selekcia RULETA
    sum = 0
    for i in act_pop:   # ziskam sucet vsetkych ciest v populacii
        sum += i.value_path

    probability = []
    for i in act_pop:   # pridam do listu vsetky fitness hodnoty v populacii
        probability.append(i.value_path)

    probability.reverse()   # zoradim od najvyssieho po najnizsiu
    # tu sa snazim simulovat to ze cim lepsi fitness, tym lepsia sanca takym sposobom, ze reversnem list hodnot
    # najvyssia hodnota bude na zaciatku a vyberiem nahodne cislo a v ktorom intervale sa bude nachadzat tak ten index vyberiem

    pick = random.randint(0, int(sum))  # nahodny vyber cisla, podla ktoreho vyberiem vyhercu
    index = 0
    for i in range(0, len(probability), 1): # hladam, v ktorom intervale sa nachadza nahodne vylosovane cislo
        pick -= probability[i]
        if (pick <= 0): # ak je mensie ako 0, znamena to ze je to vyherny interval
            index = i
            break

    return act_pop[index]

""" KRIZENIE  """
def crossover(parent1, parent2):  # funkcia krizenia pre vytvaranie potomka z dvoch parentov
    offspring = []
    substring = []
    p1 = parent1.path.copy()
    p2 = parent2.path.copy()

    index1 = random.randint(0, len(parent1.path) - 1)
    index2 = random.randint(0, len(parent1.path) - 1)
    # nahodne si urcim dve cisla a ziskam nejaky range medzi 2 indexami
    start = min(index1, index2)
    finish = max(index1, index2)

    for i in range(start, finish, 1):   # vyberiem hodnoty, ktore sa nachadzaju v danom rozmedzi z P1
        substring.append(p1[i])
        p2.remove(p1[i])

    substring.reverse() # tento substring z P1 reversnem

    # prvky z P1 vlozim do potomka na indexy odkial som ich zobral a doplnim o hodnoty z P2
    j = 0
    for i in range(0, start, 1):
        offspring.append(p2[j])
        j += 1
    for i in range(0, len(substring), 1):
        offspring.append(substring[i])

    for i in range(finish, len(p1), 1):
        offspring.append(p2[j])
        j += 1

    new_offspring = Route(offspring)
    return new_offspring

""" MUTACIA     """
def mutation(pop, mutat_rate):  # simulacia mutacie = SWAP
    for i in range(0, len(pop), 1): # prechadzam celou generaciou
        chance = random.random()    # nejaka nahodna sanca (generuje cislo 0-1)
        if (chance < mutat_rate):   # ak sa postasti, tak iba zamenim nahodny index s jeho susedom
            random_index = random.randint(1, len(pop[i].path) - 2)
            temp = pop[i].path[random_index]
            pop[i].path[random_index] = pop[i].path[random_index + 1]
            pop[i].path[random_index + 1] = temp

    return pop

def genetic_algorithm(generation, selection,cities,elite_num, random_num,mutation_yn,mutat_rate):   # hlavny algoritmus
    new_population = []

    if (elite_num > 0):     # ak sme vybrali elitizmus, tak prenesiem X najlepsich prvkov do dalsej generacie
        for i in range(0, elite_num, 1):
            new_population.append(generation[i])


    if (random_num > 0):    # ak sme vybrali aj random, tak vytvorim X nahodnych prvkov do dalsej generacie
        for _ in range(0, random_num, 1):
            new_random = Route(create_route(cities))
            new_population.append(new_random)

    if (selection == 1):    # ak sme vybrali selekciu ruletou, vyberiem 2 parentov a skrizim ich
        for _ in range(0, len(generation) - elite_num - random_num, 1):
            parent1 = rulette(generation)
            parent2 = rulette(generation)

            offspring = crossover(parent1, parent2)

            new_population.append(offspring)

    elif (selection == 2):  # ak sme vybrali selekciu turnajom, vyberiem 2 parentov a skrizim ich
        for _ in range(0, len(generation) - elite_num - random_num, 1):  #
            parent1 = tournament(generation, 5)
            parent2 = tournament(generation, 5)

            offspring = crossover(parent1, parent2)
            new_population.append(offspring)

    if (mutation_yn):   # ked uz mam celu novu generaciu, tak nad nou urobim este mutaciu
        new_population = mutation(new_population, mutat_rate)

    ranked_generation = fitness(new_population)  # vyhodnoti hodnoty ciest a zoradi od najlepsej
    #print(str(ranked_generation[0].value_path) + " " + str(average(ranked_generation))) #
    return ranked_generation

"""     POMOCNY VYPIS      """
def vypis(best, cislo):
    print("Generation: " + str(cislo))
    print("Best fitness: " + str(best.value_path))
    print("Path: ", end=" ")
    for i in best.path:
        print(i.introduce(), end=" | ")
    print("\n===================================================================================================================")

def average(pop):
    avg_value = 0
    for i in pop:
        avg_value += i.value_path
    avg_value = avg_value / len(pop)
    return round(avg_value,2)



# prednastaveny list, sluzil iba na objektivne testovanie, aby vzdy boli rovnake mesta
input1 = [
        City(3,167), City(200,33), City(72,1), City(1,1), City(87,193),
        City(44,7), City(103,26), City(200,199), City(0,199), City(56,91),
        City(144, 62), City(80, 0), City(20, 50), City(23, 69), City(175,34),
        City(10,20), City(25, 135), City(21, 88), City(14, 53), City(31,198)
        ]





cities = []
size_area = 200


while (True):   # MENU2
    best = None  # pomoccne pre ulozenie najlepsej cesty z pomedzi vsetkzch generacii
    best_generation = int(0)  # poradie generacie v ktorej sa nasiel najlepsi
    cities.clear()
    vstup = input("1 - automaticka generacia / 2 - prednastavena generacia / q - ukonci: ")
    if (vstup == "1" or vstup == "2"):
        mutation_rate = float()

        size_population = int(input("Velkost populacie (20-100): "))
        if (vstup == "1"):
            number_cities = int(input("Kolko miest(genov) vygenerovat(10-30): "))
        size_elite = int(input("Elitizmus(0-20): "))
        size_random = int(input("Random(0-20): "))
        type_of_selection = int(input("1 - ruleta / 2 - turnaj: "))
        mutation_apply = int(input("1 - ano / 0 - nie: "))
        if (mutation_apply):
            mutation_rate = float(input("Mutacia rate(0.05 = 5 %): "))
        number_generations = int(input("Pocet generacii: "))

        if (vstup == "1"):
            cities = create_cities(number_cities, size_area)
            first_population = create_population(size_population, cities)
            best = first_population[0]
            best_generation = 0
            act_population = None
            for i in range(0, number_generations, 1):
                if (i == 0):
                    print("\n\n")
                    vypis(first_population[0], 0)
                    act_population = genetic_algorithm(first_population,type_of_selection, cities, size_elite, size_random, mutation_apply, mutation_rate)
                    if (act_population[0].value_path < best.value_path):
                        best = act_population[0]
                        best_generation = i + 1
                    #vypis(act_population[0],i + 1)
                else:
                    act_population = genetic_algorithm(act_population, type_of_selection, cities, size_elite, size_random, mutation_apply, mutation_rate)
                    if (act_population[0].value_path < best.value_path):
                        best = act_population[0]
                        best_generation = i + 1
                    if (i == number_generations - 1):
                        vypis(act_population[0], i + 1)
                        print("***** CELKOVA NAJLEPSIA CESTA NAJDENA *****")
                        vypis(best, best_generation)
        elif (vstup == "2"):
            cities = input1.copy()
            first_population = create_population(size_population, cities)
            best = first_population[0]
            best_generation = 0
            act_population = None
            for i in range(0, number_generations, 1):
                if (i == 0):
                    act_population = genetic_algorithm(first_population, type_of_selection, cities, size_elite, size_random, mutation_apply, mutation_rate)
                    if (act_population[0].value_path < best.value_path):
                        best = act_population[0]
                        best_generation = i + 1
                    vypis(act_population[0],i + 1)
                else:
                    act_population = genetic_algorithm(act_population, type_of_selection, cities, size_elite, size_random, mutation_apply, mutation_rate)
                    if (act_population[0].value_path < best.value_path):
                        best = act_population[0]
                        best_generation = i + 1
                    if (i == number_generations - 1):
                        vypis(act_population[0], i + 1)
                        print("***** CELKOVA NAJLEPSIA CESTA NAJDENA *****")
                        vypis(best, best_generation)

    elif (vstup == "q"):
        exit()