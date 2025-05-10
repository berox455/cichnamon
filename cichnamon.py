import random
import copy
import os
import jsonpickle #both are for saving and importing progress
import glob #used for quick import
from numpy.random import choice #to help with generating weighted choices from an array

TYPE_ADVANTEGES = { #used in damage calculation
    "water":"fire",
    "fire":"grass",
    "grass":"water"
}

#contains all cichnamon species and their types
CICH_EXI = {
    "Melon":"water",
    "Demon":"fire",
    "Rose":"grass",
    "Plum":"water",
    "Gekko":"fire",
    "Poppy":"grass",
    "Kiwi":"water",
    "Chameleon":"fire",
    "Dandelion":"grass",
    "Durian":"water",
    "Dragon":"fire",
    "Lily":"grass"
}

cichnamons = [] #contains created cichnamon
trainers = [] #contains created trainers

class Cichnamon:
    def __init__(self, name, type, level = 5, xp = 0, base_attack = 20, base_hp = 20, base_special_attack = 20, base_defense = 20, base_special_defense = 20, hp = None):
        self.name = name[0].upper() + name[1:].lower()
        self.type = type.lower()
        self.lvl = level
        self.max_xp = self.lvl**3 #xp to level up
        self.xp = xp
        self.base_hp = base_hp
        self.max_hp = round((((self.base_hp + 2) * 2 * self.lvl)/100), 0) + self.lvl + 10
        if hp == None:
            self.hp = self.max_hp
        else:
            self.hp = hp
        self.base_attack = base_attack
        self.attack = round((((self.base_attack + 2) * 2 * self.lvl)/100), 0) + 5
        self.base_sp_attack = base_special_attack
        self.sp_attack = round((((self.base_sp_attack + 2) * 2 * self.lvl)/100), 0) + 5
        self.base_defense = base_defense
        self.defense = round((((self.base_defense + 2) * 2 * self.lvl)/100), 0) + 5
        self.base_sp_defense = base_special_defense
        self.sp_defense = round((((self.base_sp_defense + 2) * 2 * self.lvl)/100), 0) + 5
        self.shield = 0
        self.shield_cooldown = 0
        self.move_set = []
        self.owner = None
        cichnamons.append(self)
        self.add_move(tackle)

        
    def __del__(self):
        print(self.name, "died!")


    def add_owner(self, trainer):
        if trainer in trainers:
            trainer.add_cichnamon(self)
        else:
            print(trainer, "is non-existent!!")

    
    def do_sp_attack(self, enemy, move):
        damage = (self.sp_attack) * 1.2 * move.damage #damage is multiplied depending on cichnamons attack stat
        
        damage = move.attack_multiplier(enemy, damage)
        
        return round(damage / (enemy.sp_defense * 1.2), 0) #the more defense an enemy cichnamon has, the less damage it will recieve

        
    def do_attack(self, enemy, move):
        damage = (self.attack) * 1.1 * move.damage #damage is multiplied depending on cichnamons attack stat

        damage = move.attack_multiplier(enemy, damage)

        return round(damage / (enemy.defense * 1.1), 0) #the more defense an enemy cichnamon has, the less damage it will recieve


    def hit_yourself(self, move):
        if move.special:
            self.hp -= self.do_sp_attack(self, move)
        else:
            self.hp -= self.do_attack(self, move)
        

    def go_attack(self, enemy, move): #makes a cichnamon attack another cichnamon
        if enemy not in cichnamons or move not in self.move_set or move.charge < 1 or enemy.faint() == True:
            #debug
            print("---\nATTACK ERROR\n---")
            return False #for determining if the attack went through
        else:
            #later remove prints and add them to the final process + add crit chance
            print("--- Attack ---\n")
            print(self.name, "is using", move.name, "to attack", enemy.name, "\n")
            

            if move.hits() is False:
                print("Missed!!", end="")
                input("...")
            else:
                if move.special:
                    if self.sp_attack < 0.5 * enemy.sp_defense:
                        self.hit_yourself(move)
                    else:
                        if enemy.shield <= 0:
                            temphp = enemy.hp
                            enemy.hp -= self.do_sp_attack(enemy, move)
                            print(temphp - enemy.hp, "damage dealt", end="")
                            input("...")
                        else:
                            temphp = enemy.hp + enemy.shield
                            enemy.shield -= self.do_sp_attack(enemy, move)

                            if enemy.shield < 0:
                                enemy.hp += enemy.shield
                                enemy.shield = 0

                            print(temphp - enemy.hp - enemy.shield, "damage dealt", end="")
                            input("...")

                        
                else:
                    if self.attack < 0.5 * enemy.defense:
                        self.hit_yourself(move)
                    else:
                        if enemy.shield <= 0:
                            temphp = enemy.hp + enemy.shield
                            enemy.hp -= self.do_attack(enemy, move)
                            print(temphp - enemy.hp - enemy.shield, "damage dealt", end="")
                            input("...")
                        else:
                            temphp = enemy.hp + enemy.shield
                            enemy.shield -= self.do_attack(enemy, move)

                            if enemy.shield < 0:
                                enemy.hp += enemy.shield
                                enemy.shield = 0

                            print(temphp - enemy.hp - enemy.shield, "damage dealt", end="")
                            input("...")

            move.charge -= 1 #after an attack it's charge is decreased by 1

        print("---------------------------------\n")

        return True #for determining if the attack went through


    def check_adsr(self, adsr, shield_cooldown = 0): #chcecks input for adsr, explanation bellow in choose_adsr
        if adsr.isdigit() is False:
            print("~~~\nPlease enter a number!\n~~~")
            return True, shield_cooldown
        elif int(adsr) < 1 or int(adsr) > 4:
            print("~~~\nPlease enter a number between 1 and 4\n~~~")
            return True, shield_cooldown
        elif int(adsr) == 2 and self.shield > 0:
            print("~~~\nYou can only choose defense if your cichnamons defense has become zero!!\n~~~")
            return True, shield_cooldown
        elif int(adsr) == 3 and len(self.owner.owned_cichnamon) == 1:
            print("~~~\nYou can only switch if you have more than 1 cichanmon!!\n~~~")
            return True, shield_cooldown
        elif int(adsr) == 2 and shield_cooldown > 0:
            print("~~~\nShield is on cooldown, ", shield_cooldown, " turn(s) left!!\n~~~", sep="")
            return True, shield_cooldown
        else:
            if int(adsr) == 2:
                shield_cooldown = 2
                return False, shield_cooldown
            else:
                shield_cooldown -= 1
                return False, shield_cooldown

    
    def choose_adsr(self): #makes you choose between attack, defense, switch and run
        shield_cooldown = self.shield_cooldown
        check = [True, shield_cooldown]
        while check[0]:
            adsr = input("\t[1] for attack\n\t[2] for defense\n\t[3] to switch your Cichnamon\n\t[4] to run away\nChoose one: ")
            check = self.check_adsr(adsr, shield_cooldown)
                
        adsr = int(adsr)
        self.shield_cooldown = check[1]
                
        return adsr


    def check_choice(self, choice):
        if choice.isdigit() is False:
            print("Please enter a number!")
            return True
        elif int(choice) < 0 or int(choice) > len(self.move_set):
            print("Please enter a number between 0 and", len(self.move_set))
            return True
        else:
            return False


    def battle_client(self, enemy, wild = False):
        print("\n\n--- ", self.name, "'s move ---", sep="")
        
        print()
        self.show_stats()
        print()
        if wild:
            if random.random() <= 0.98:
                self_adsr = 1
            else:
                self_adsr = 4
        else:
            self_adsr = self.choose_adsr()
        if self_adsr == 1:
            print("\n\n")

            if wild:
                choice = random.randint(0, len(self.move_set) - 1)
                attacked = self.go_attack(enemy, self.move_set[choice-1])
                
                while attacked is False:
                    choice = random.int(len(self.move_set - 1))
                    attacked = self.go_attack(enemy, self.move_set[choice-1])
            else:
                self.show_move_set()
                choice = input("Choose a move or go back with[0]: ")
                while self.check_choice(choice):
                    choice = input("Choose a move or go back with[0](again): ")
                choice = int(choice)
                print()
                if choice == 0:
                    return True, "back"
                elif self.go_attack(enemy, self.move_set[choice-1]) is False:
                    print("You aren't able to choose this move!!!")
        elif self_adsr == 2:
            self.shield += self.defense
            print("\n---")
            print(self.name, "has decided to be defensive and added", self.defense, "shield")
            input("...")
            print("---------------------------------\n")
        elif self_adsr == 3:
            print()
            print(self.owner.name, "decided to switch Cichnamon!")
            input("...")
            print("-----\n")
            return False, "switch" #switch after this one
        elif self_adsr == 4:
            print()
            if wild:
                print(self.name, "is running away!!")
            else:
                print(self.owner.name, "is trying to abandon the match!!")
            input("...")
            print()
            return False, "run"
                    
            
        if enemy.faint():
            print(enemy.name, "fainted.")
            input("...\n")
            self.add_xp(enemy)
            if self.level_up():
                print(self.name, "leveled up!!!")
                input("...")

            return True, "attack"

        return True, "attack"


    def battle(self, enemy, wild = False):
        switch = ""
        self_continue = [None, None]
        enemy_continue = [None, None]
        
        print("\n\n")

        if enemy.faint() is False and self.faint() is False:
            self.show_stats(show_advanced=True)
            print("\n|VS|\n")
            if wild:
                enemy.show_stats(show_advanced=True, wild = True)
            else:
                enemy.show_stats(show_advanced=True)
            print()

            while enemy.faint() is False and self.faint() is False:
                self_continue = self.battle_client(enemy)

                while self_continue and self_continue[1] == "back":
                    self_continue = self.battle_client(enemy)

                if enemy.faint() is False:
                    if wild:
                        enemy_continue = enemy.battle_client(self, wild = True)
                    else:
                        enemy_continue = enemy.battle_client(self)

                    while enemy_continue and enemy_continue[1] == "back":
                        if wild:
                            enemy_continue = enemy.battle_client(self, wild = True)
                        else:
                            enemy_continue = enemy.battle_client(self)

                    if self.faint():
                        break
                else:
                    break
                if self_continue[0] is False or enemy_continue[0] is False:
                    if self_continue[0] is False:
                        if self_continue[1] == "switch":
                            switch = "self"
                        elif self_continue[1] == "run":
                            return False, "self"

                    if enemy_continue[0] is False:
                        if enemy_continue[1] == "switch":
                            switch += "enemy"
                        elif enemy_continue[1] == "run":
                            return False, "enemy"
                    
                    break

            if enemy.faint() or (enemy_continue[0] and enemy_continue[1] == "attack"):
                if wild:
                    enemy.show_stats(show_advanced=True, wild = True)
                else:
                    enemy.show_stats(show_advanced=True)
            if self.faint() or (self_continue[0] and self_continue[1] == "attack"):
                self.show_stats(show_advanced=True)

        elif enemy.faint():
            print(enemy.name, "already fainted!!!")
            print("You cannot fight with or against a fainted pokemon!!!")

        elif self.faint():
            print(self.name, "already fainted!!!")
            print("You cannot fight with or against a fainted pokemon!!!")
        else:
            print("Idk what is wrong")

        print("\n\n")

        if self_continue[0] is False or enemy_continue[0] is False:
            return True, switch
        else:
            return False, switch


    def add_xp(self, enemy):
        gained_xp = round(64 * enemy.lvl / 7, 0)
        self.xp += gained_xp
        print(self.name, "gained", int(gained_xp), "xp!!")
        input("...")
        print()


    def level_up(self):
        if self.xp >= self.max_xp:
            self.xp -= self.max_xp
            self.lvl += 1
            self.max_xp = self.lvl**3
            self.attack = round((((self.base_attack + 2) * 2 * self.lvl)/100), 0) + 5
            self.sp_attack = round((((self.base_sp_attack + 2) * 2 * self.lvl)/100), 0) + 5
            self.defense = round((((self.base_defense + 2) * 2 * self.lvl)/100), 0) + 5
            self.sp_defense = round((((self.base_sp_defense + 2) * 2 * self.lvl)/100), 0) + 5

            variable = self.max_hp #for calculating hp a Cichnamon gets after level up
            self.max_hp = round((((self.base_hp + 2) * 2 * self.lvl)/100), 0) + self.lvl + 10
            self.hp += self.max_hp - variable

            return True
        else:
            return False


    def faint(self):
        if self.hp <= 0:
            self.hp = 0
            return True
        else:
            return False

    
    def add_move(self, move):
        move_copy = copy.copy(move)
        if len(self.move_set) == 4:
            return
        else:
            if move_copy.type == self.type:
                move_copy.damage *= 1.5
            self.move_set.append(move_copy)
            move.used_by.append(self)

    
    def restoration(self):
        self.hp = self.max_hp
        for move in self.move_set:
            move.charge = move.max_charge

        print(self.name, "restored")


    def show_move_set(self):
        print()
        print("---   Move set   ---")
        print()

        if len(self.move_set) <= 0:
            print("Empty")
        else:
            i = 1

            for move in self.move_set:
                print("#", i, "\tName: ", move.name, sep="")
                print("\tType: ", move.type, "\tCharge: ", move.charge, "\tSpecial: ", move.special, "\tDamage: ", move.damage, sep="")
                if i < len(self.move_set):
                    print("")
                i+=1

        print()
        print("---              ---")


    def show_stats(self, show_move_set = False, show_advanced = False, show_cichclass = False, wild = False):
        print("\t--- Stats ---")

        if show_advanced:
            print("Name:", self.name)
            print("Type:", self.type)
            if wild is False:
                print("Cichnamon:", self.cich_class)
            print("Lvl:", int(self.lvl))
            print("Max hp:", int(self.max_hp))
            print("Hp:", int(self.hp))
            if wild is False:
                print("Shield:", int(self.shield))
            print("Attack:", int(self.attack))
            print("Defense:", int(self.defense))
            print("Sp_attack:", int(self.sp_attack))
            print("Sp_defense:", int(self.sp_defense))
            if wild is False:
                print("Xp required to lvl up:", int(self.max_xp))
                print("Xp:", round(self.xp, 0))
            print("---------------------------------")
        else:
            print("Name:", self.name, end="\t")
            print("Type:", self.type)

            if wild is False:
                if show_cichclass:
                    print("Cichnamon:", self.cich_class)

                print("Hp:", int(self.hp), "/", int(self.max_hp), end="\t")

                if self.shield > 0:
                    print("+", int(self.shield))
                else:
                    print()
            
                print("Lvl:", self.lvl, end="\t")
                print("Xp:", round(self.xp, 0), "/", int(self.max_xp))
            else:
                print("Lvl:", int(self.lvl), "\tHp:", self.hp, "/", self.max_hp)
            print("---------------------------------")


        if show_move_set:
            self.show_move_set()


class Melon(Cichnamon):
    def __init__(self, name, level = 5, xp = 0, hp = None):
        super().__init__(name, "water", level, xp, base_attack = 20, base_hp = 25, base_special_attack = 20, base_defense = 25, base_special_defense = 20, hp = hp)
        self.cich_class = "Melon"
        self.add_move(roll)
        if self.lvl == 8:
            self.add_move(water_slap)

    
    def level_up(self):
        if super().level_up():
            if self.lvl == 8:
                self.add_move(water_slap)
                print("\n", self.name, "gained a move:", water_slap.name, "\n")
            return True
        else:
            return False


class Plum(Cichnamon):
    def __init__(self, name, level = 5, xp = 0, hp = None):
        super().__init__(name, "water", level, xp, base_attack = 20, base_hp = 25, base_special_attack = 20, base_defense = 20, base_special_defense = 25, hp = hp)
        self.cich_class = "Plum"
        self.add_move(roll)
        if self.lvl == 8:
            self.add_move(mini_vortex)

    
    def level_up(self):
        if super().level_up():
            if self.lvl == 8:
                self.add_move(mini_vortex)
                print("\n", self.name, "gained a move:", mini_vortex.name, "\n")
            return True
        else:
            return False


class Kiwi(Cichnamon):
    def __init__(self, name, level = 5, xp = 0, hp = None):
        super().__init__(name, "water", level, xp, base_attack = 22, base_hp = 18, base_special_attack = 26, base_defense = 22, base_special_defense = 22, hp = hp)
        self.cich_class = "Kiwi"
        self.add_move(roll)
        if self.lvl == 8:
            self.add_move(water_gun)

    
    def level_up(self):
        if super().level_up():
            if self.lvl == 8:
                self.add_move(water_gun)
                print("\n", self.name, "gained a move:", water_gun.name, "\n")
            return True
        else:
            return False


class Durian(Cichnamon):
    def __init__(self, name, level = 5, xp = 0, hp = None):
        super().__init__(name, "water", level, xp, base_attack = 20, base_hp = 20, base_special_attack = 30, base_defense = 20, base_special_defense = 20, hp = hp)
        self.cich_class = "Durian"
        self.add_move(roll)
        if self.lvl == 8:
            self.add_move(smell_overpower)

    
    def level_up(self):
        if super().level_up():
            if self.lvl == 8:
                self.add_move(smell_overpower)
                print("\n", self.name, "gained a move:", smell_overpower.name, "\n")
            return True
        else:
            return False


class Demon(Cichnamon):
    def __init__(self, name, level = 5, xp = 0, hp = None):
        super().__init__(name, "fire", level, xp, base_attack = 34, base_hp = 18, base_special_attack = 22, base_defense = 18, base_special_defense = 18, hp = hp)
        self.cich_class = "Demon"
        self.add_move(bite)
        if self.lvl == 8:
            self.add_move(fire_fist)

    
    def level_up(self):
        if super().level_up():
            if self.lvl == 8:
                self.add_move(fire_fist)
                print("\n", self.name, "gained a move:", fire_fist.name, "\n")
            return True
        else:
            return False


class Gekko(Cichnamon):
    def __init__(self, name, level = 5, xp = 0, hp = None):
        super().__init__(name, "fire", level, xp, base_attack = 26, base_hp = 18, base_special_attack = 26, base_defense = 20, base_special_defense = 20, hp = hp)
        self.cich_class = "Gekko"
        self.add_move(bite)
        if self.lvl == 8:
            self.add_move(whip)

    
    def level_up(self):
        if super().level_up():
            if self.lvl == 8:
                self.add_move(whip)
                print("\n", self.name, "gained a move:", whip.name, "\n")
            return True
        else:
            return False


class Chameleon(Cichnamon):
    def __init__(self, name, level = 5, xp = 0, hp = None):
        super().__init__(name, "fire", level, xp, base_attack = 20, base_hp = 18, base_special_attack = 32, base_defense = 20, base_special_defense = 20, hp = hp)
        self.cich_class = "Chameleon"
        self.add_move(bite)
        if self.lvl == 8:
            self.add_move(burning_lick)

    
    def level_up(self):
        if super().level_up():
            if self.lvl == 8:
                self.add_move(burning_lick)
                print("\n", self.name, "gained a move:", burning_lick.name, "\n")
            return True
        else:
            return False


class Dragon(Cichnamon):
    def __init__(self, name, level = 5, xp = 0, hp = None):
        super().__init__(name, "fire", level, xp, base_attack = 24, base_hp = 18, base_special_attack = 24, base_defense = 22, base_special_defense = 22, hp = hp)
        self.cich_class = "Dragon"
        self.add_move(bite)
        if self.lvl == 8:
            self.add_move(fireball)

    
    def level_up(self):
        if super().level_up():
            if self.lvl == 8:
                self.add_move(fireball)
                print("\n", self.name, "gained a move:", fireball.name, "\n")
            return True
        else:
            return False


class Rose(Cichnamon):
    def __init__(self, name, level = 5, xp = 0, hp = None):
        super().__init__(name, "grass", level, xp, base_attack = 30, base_hp = 14, base_special_attack = 20, base_defense = 23, base_special_defense = 23, hp = hp)
        self.cich_class = "Rose"
        self.add_move(touch_of_beauty)
        if self.lvl == 8:
            self.add_move(thorns)

    
    def level_up(self):
        if super().level_up():
            if self.lvl == 8:
                self.add_move(thorns)
                print("\n", self.name, "gained a move:", thorns.name, "\n")
            return True
        else:
            return False


class Poppy(Cichnamon):
    def __init__(self, name, level = 5, xp = 0, hp = None):
        super().__init__(name, "grass", level, xp, base_attack = 18, base_hp = 20, base_special_attack = 30, base_defense = 18, base_special_defense = 24, hp = hp)
        self.cich_class = "Poppy"
        self.add_move(touch_of_beauty)
        if self.lvl == 8:
            self.add_move(leaf_shuriken)

    
    def level_up(self):
        if super().level_up():
            if self.lvl == 8:
                self.add_move(leaf_shuriken)
                print("\n", self.name, "gained a move:", leaf_shuriken.name, "\n")
            return True
        else:
            return False


class Dandelion(Cichnamon):
    def __init__(self, name, level = 5, xp = 0, hp = None):
        super().__init__(name, "grass", level, xp, base_attack = 18, base_hp = 24, base_special_attack = 26, base_defense = 18, base_special_defense = 24, hp = hp)
        self.cich_class = "Dandelion"
        self.add_move(touch_of_beauty)
        if self.lvl == 8:
            self.add_move(seed_bombs)

    
    def level_up(self):
        if super().level_up():
            if self.lvl == 8:
                self.add_move(seed_bombs)
                print("\n", self.name, "gained a move:", seed_bombs.name, "\n")
                return True
        else:
            return False


class Lily(Cichnamon):
    def __init__(self, name, level = 5, xp = 0, hp = None):
        super().__init__(name, "grass", level, xp, base_attack = 20, base_hp = 20, base_special_attack = 28, base_defense = 18, base_special_defense = 24
        , hp = hp)
        self.cich_class = "Lily"
        self.add_move(touch_of_beauty)
        if self.lvl == 8:
            self.add_move(cuteness_overload)

    
    def level_up(self):
        if super().level_up():
            if self.lvl == 8:
                self.add_move(cuteness_overload)
                print("\n", self.name, "gained a move:", cuteness_overload.name, "\n")
                return True
        else:
            return False


class Move:
    def __init__(self, name = "Name", type = "type", charge = 20, special = False, damage = 2, accuracy = 0.8, crit_chance = 0.04):
        self.name = name[0].upper() + name[1:].lower()
        self.type = type.lower()
        self.max_charge = charge #the number of times the move can be used in battle
        self.charge = self.max_charge #every time it is used, it goes down by one
        self.special = special
        self.damage = damage
        self.accuracy = accuracy
        self.crit_chance = crit_chance
        self.used_by = []

        
    def __del__(self): 
        print(self.name, "has been destroyed!")


    def hits(self):
        if random.random() <= self.accuracy:
            return True
        else:
            return False


    def crits(self):
        if random.random() <= self.crit_chance:
            return True
        else:
            return False


    def attack_multiplier(self, enemy, damage):
        if self.type == enemy.type or TYPE_ADVANTEGES.get(enemy.type) == self.type: #if the move is the same type as the enemy, then it's not effective and the damage goes down
            damage /= 2
            print("Not effective!")

        elif TYPE_ADVANTEGES.get(self.type) == enemy.type: #if there is a type advantage the damage is doubled
            damage *= 2
            print("Super effective!")

        if self.crits():
            damage *= 2
            print("It's a crit!!")
        
        return damage


class Trainer:
    def __init__(self, name):
        self.name = name[0].upper() + name[1:].lower()
        self.fights = 0
        self.won_fights = 0
        self.fights_wild = 0
        self.fights_won_wild = 0
        self.money = 3000
        self.owned_cichnamon = []
        self.cichbox = []
        trainers.append(self)

    
    def __del__(self):
        if self.money < 0:
            if random.random() <= 0.5:
                print(self.name, "died from money deficiency!!")
            else:
                print(self.name, "couldn't even buy food and so... he died!!")
        else:
            print(self.name, "died!")
        

    def save_trainer(self):
        with open(self.name + "_settings.json", "w") as f:
            f.write(jsonpickle.encode(self, False, max_depth=3, indent=4))

    
    def load_trainer(self):
        if os.access(self.name + "_settings.json", os.F_OK):
            with open(self.name + "_settings.json", "r") as f:
                settings = jsonpickle.decode(f.read())
                self.name = settings["name"]
                self.fights = settings["fights"]
                self.won_fights = settings["won_fights"]
                self.money = settings["money"]

                for owned_cichnamon in settings["owned_cichnamon"]:
                    cichnamon = create_cichnamon(owned_cichnamon["cich_class"], owned_cichnamon["name"], owned_cichnamon["lvl"], owned_cichnamon["xp"], owned_cichnamon["hp"])
                    self.add_cichnamon(cichnamon)
                    
                for boxed_cichnamon in settings["cichbox"]:
                    cichnamon = create_cichnamon(boxed_cichnamon["cich_class"], boxed_cichnamon["name"], boxed_cichnamon["lvl"], boxed_cichnamon["xp"], boxed_cichnamon["hp"])
                    cichnamon.owner = self
                    self.cichbox.append(cichnamon)

            return True
        else:
            print("Trainer not found!\n")
            del trainers[:len(trainers)]
            return False


    def get_winrate(self):
        if self.fights < 1:
            return 0
        else:
            return round(self.won_fights / self.fights, 2)*100


    def get_wild_winrate(self):
        if self.fights_wild < 1:
            return 0
        else:
            return round(self.fights_won_wild / self.fights_wild, 2)*100


    def add_cichnamon(self, cichnamon):
        if len(self.owned_cichnamon) == 6:
            self.cichbox.append(cichnamon)
            print("Oh, oh. You've reached the limit of Cichnamon, which you can carry with you.")
            print("Cichnamon has been added to Cichbox!")
            cichnamon.owner = self
        elif cichnamon in cichnamons:
            self.owned_cichnamon.append(cichnamon)
            cichnamon.owner = self


    def cichbox_move(self, first_opened = True):
        print()
        if first_opened:
            print("You opened up the cichbox!!")
        num = 0

        while num < 1 or num > 3:
            print("\t[1]Take out a Cichnamon")
            print("\t[2]Put a Cichnamon inside")
            print("\t[3]Exit cichbox")
            num = get_num("\nChoose:\t", True)

        if num == 1:
            if len(self.cichbox) > 0:
                i = 1
                print()
                for cichnamon in self.cichbox:
                    if i != len(self.cichbox):
                        print("[" + str(i) + "] ", end="")
                        cichnamon.show_stats()
                        print(", ")

                    else:
                        print("[" + str(i) + "] ", end="")
                        cichnamon.show_stats()
                    i += 1

                cich_num = get_num("Which Cichnamon do you want to take out? [0 to go back]")

                while cich_num < 0 or cich_num > len(self.cichbox):
                    cich_num = get_num("Which Cichnamon do you want to take out? [0 to go back](again)")

                if cich_num == 0:
                    print("You return back.")
                else:
                    self.add_cichnamon(self.cichbox.pop(cich_num - 1))
            else:
                print("You don't have any Cichnamon inside the cichbox!!") 
            return True
        elif num == 2:
            if len(self.owned_cichnamon) > 1:
                self.show_owned_cichnamon()

                cich_num = get_num("Which Cichnamon do you want to put in the cichbox? [0 to go back]")

                while cich_num < 0 or cich_num > len(self.owned_cichnamon):
                    cich_num = get_num("Which Cichnamon do you want to put in the cichbox? [0 to go back](again)")

                if cich_num == 0:
                    print("You return back.")
                else:
                    self.cichbox.append(self.owned_cichnamon.pop(cich_num - 1))
            else:
                print("You can't put your only Cichnamon into the cichbox!!")
                print("You can only put a Cichnamon inside, if you have more than one with you!!")
            return True
        elif num == 3:
            print("You exit the cichbox\n")


    def remove_cichnamon(self, cichnamon):
        if cichnamon in self.owned_cichnamon:
            self.owned_cichnamon.remove(cichnamon)
            cichnamon.owner = None
        else:
            print("Couldn't remove", cichnamon)
            return


    def defeated(self):
        num_fainted = 0 #for calculation of fainted cichnamon

        for cichnamon in self.owned_cichnamon:
            if cichnamon.faint():
                num_fainted += 1

        if len(self.owned_cichnamon) == num_fainted:
            if self.money < 0:
                del self
            return True
        else:
            return False

    
    def owned_cichnamon_restoration(self):
        print("\n----", self.name, "Restoration ----\n")
        for cichnamon in self.owned_cichnamon:
            cichnamon.restoration()
        print("\nAll Cichnamon restored!!")
        print("---------------------\n")


    def get_average_cichnamon_lvl(self):
        length = len(self.owned_cichnamon)
        combined_lvl = 0

        for cichnamon in self.owned_cichnamon:
            combined_lvl += cichnamon.lvl

        return round(combined_lvl / length, 0)

    
    def check_choice(self, choice): #used to check if chosen cichnamon in battle can indeed be chosen
        if choice.isdigit() is False:
            print("Please enter a number!")
            return True
        elif int(choice) < 1 or int(choice) > len(self.owned_cichnamon):
            print("Please enter a number between 1 and", len(self.owned_cichnamon))
            return True
        else:
            return False


    def fight_client(self):
        print("\t", "--- ", self.name, "'s turn ---", sep="")
        print()
        self.show_owned_cichnamon()
        choice = input("Choose a cichnamon: ")
        while self.check_choice(choice):
            choice = input("Choose a cichnamon(again): ")
    
        print()
        return int(choice)


    def fight(self, enemy_trainer):
        run_or_switch = [None, None]

        if enemy_trainer not in trainers:
            print("Couldn't fight",enemy_trainer, "they're non-existent")
            return
        elif len(self.owned_cichnamon) < 1:
            print("Can't fight without a cichnamon to fight with!!")
            return
        elif len(enemy_trainer.owned_cichnamon) < 1:
            print("Can't fight a trainer, who doesn't own any cichnamon!!")
            return
        elif enemy_trainer.defeated() or self.defeated():
            print("You can't fight with or against a trainer with all fainted Cichnamon!!")
            return
        else:
            print("\n\n\t\t\t--- Fight ---")
            print(self.name, "|VS|", enemy_trainer.name, "\n\n")
            self.show_stats()
            print("\n\n")
            enemy_trainer.show_stats()
            print()

            variable = 0 #used to help with run_or_switch

            while enemy_trainer.defeated() is False and self.defeated() is False:
                if variable > 0:
                    if run_or_switch[0]:
                        print()
                        if run_or_switch[1] == "selfenemy":
                            self_choice = self.fight_client()
                            enemy_choice = enemy_trainer.fight_client()
                        elif run_or_switch[1] == "self":
                            self_choice = self.fight_client()
                        elif run_or_switch[1] == "enemy":
                            enemy_choice = enemy_trainer.fight_client()
                        else:
                            print("\n~Cichnamon fainted while trying to switch~\n")
                    else:
                        self_choice = self.fight_client()
                        enemy_choice = enemy_trainer.fight_client()
                else:
                    self_choice = self.fight_client()
                    enemy_choice = enemy_trainer.fight_client()

                run_or_switch = self.owned_cichnamon[self_choice-1].battle(enemy_trainer.owned_cichnamon[enemy_choice-1])

                if run_or_switch[0] is False and run_or_switch[1] != "":
                    print(run_or_switch, "Yup there is a problem")
                    break

                variable += 1


            if run_or_switch[1] == "self":
                print(self.name, "has decided to run instead of fighting!!")
                print("This means that", enemy_trainer.name, "has won the match!!")

                enemy_trainer.money += 450
                self.money -= 450
                enemy_trainer.won_fights += 1

            elif run_or_switch[1] == "enemy":
                print(enemy_trainer.name, "has decided to run instead of fighting!!")
                print("This means that", self.name, "has won the match!!")

                self.money += 450
                enemy_trainer.money -= 450
                self.won_fights += 1
            else:
                if self.defeated():
                    print(enemy_trainer.name, "has won the match by defeating", self.name)
                    print("Congratulations!!")
                    enemy_trainer.won_fights += 1
                    enemy_trainer.money += 300
                    self.money -= 300 
                elif enemy_trainer.defeated():
                    print(self.name, "has won the match by defeating", enemy_trainer.name)
                    print("Congratulations!!")
                    self.won_fights += 1
                    self.money += 300
                    enemy_trainer.money -= 300
                else:
                    print("Idk man, guess the fight has ended even though nobody won yet")

        #removes remaining shield from any cichnamon, which engaged in the fight
        for cichnamon in self.owned_cichnamon:
            cichnamon.shield = 0
            cichnamon.shield_cooldown = 0
        for cichnamon in enemy_trainer.owned_cichnamon:
            cichnamon.shield = 0
            cichnamon.shield_cooldown = 0

        self.fights += 1
        enemy_trainer.fights += 1

        print(r"""
             ___________
            '._==_==_=_.'
            .-\:      /-.
           | (|:.     |) |
            '-|:.     |-'
              \::.    /
               '::. .'
                 ) (
               _.' '._
              `"'"'"'"`
            """)
        input("...")

        self.show_stats(True)
        input("...")
        if self.defeated() is False:
            for cichnamon in self.owned_cichnamon:
                cichnamon.show_stats(show_advanced=True)
                input("...")

        enemy_trainer.show_stats(True)
        input("...")
        if enemy_trainer.defeated() is False:
            for cichnamon in enemy_trainer.owned_cichnamon:
                cichnamon.show_stats(show_advanced=True)
                input("...")


    def wild_fight(self, wild_cichnamon):
        print("But the wild Cichnnamon won't give up without a fight!")
        input("...")

        print("\n\n\t\t\t--- Fight ---")
        print(self.name, "|VS|", wild_cichnamon.name, "\n\n")
        self.show_stats()
        print("\n\n")
        wild_cichnamon.show_stats(wild = True)
        print()

        variable = 0 #used to help with run_or_switch
        while wild_cichnamon.faint() is False and self.defeated() is False:
            if variable > 0:
                if run_or_switch[0]:
                    if run_or_switch[1] == "self":
                        print()
                        self_choice = self.fight_client()
                    else:
                        print("\n~Cichnamon fainted while trying to switch~\n")
                elif run_or_switch[0] is False:
                    break
            else:
                self_choice = self.fight_client()
            run_or_switch = self.owned_cichnamon[self_choice-1].battle(wild_cichnamon, wild = True)

            variable += 1
        
        
        if run_or_switch[1] == "self":
            print(self.name, "has decided to run instead of fighting!!")
        elif run_or_switch[1] == "enemy":
            print("The fight ended, because the wild Cichnamon ran away!!\n\n")
        else:
            if self.defeated():
                print("You've been defeated by a wild", wild_cichnamon.name + "!\n\n")
            elif wild_cichnamon.faint():
                print("You've succesfully beaten", wild_cichnamon.name + "!\n\n")
                self.fights_won_wild += 1
            else:
                print("~~~There's a problem within def wild_fight~~~")
        
        #removes remaining shield from any cichnamon, which engaged in the fight
        for cichnamon in self.owned_cichnamon:
            if cichnamon.shield > 0:
                print(cichnamon.name, "'s shield has dissipated!\n", sep="")
                cichnamon.shield = 0
                cichnamon.shield_cooldown = 0
        wild_cichnamon.shield = 0

        self.fights_wild += 1       

        self.show_stats(True)
        input("...")
        if self.defeated() is False:
            for cichnamon in self.owned_cichnamon:
                cichnamon.show_stats(show_advanced=True)
                input("...")
        if wild_cichnamon.faint() is False:
            wild_cichnamon.show_stats(show_advanced=True, wild = True)
            input("...")

            return False

        return True


    def show_owned_cichnamon(self):
        print()
        print("--- ", self.name, "'s cichnamon ---", sep="")
        print()
        
        i = 1

        for cichnamon in self.owned_cichnamon:
            lvl = int(round(cichnamon.lvl, 0))
            hp = int(round(cichnamon.hp, 0))
            max_hp = int(round(cichnamon.max_hp, 0))
            shield = int(round(cichnamon.shield, 0))

            print("#", i, "\tName: ", cichnamon.name, "\tType: ", cichnamon.type, sep="")
            print("--", "\tLvl:", lvl, "\tHp:", hp, "/", max_hp, end="")
            if shield > 0:
                print(" +", shield, end="")
                if cichnamon.faint(): print("\tFainted")
                else: print()
            else:
                print()
            print()
            i += 1

        print("---                 ---")


    def show_stats(self, show_owned_cichnamon = False):
        print("\t--- Stats ---")
        print("Name:", self.name, end="")
        print("\t\t# of cichnamon:", len(self.owned_cichnamon))
        print("Fights:", self.fights, "Won fights:", self.won_fights, end=" ")
        print("Winrate:", self.get_winrate(), "%")
        print("Money:", self.money, "$")
        if self.fights_wild > 0:
            print("\n--- Wild stats---")
            print("Wild fights:", self.fights_wild, "Wild fights won:", self.fights_won_wild)
            print("Wild fights winrate:", self.get_wild_winrate(), "%")
        print("-----------------------------------------")

        if len(self.owned_cichnamon) > 0 and show_owned_cichnamon:
            self.show_owned_cichnamon()

        print()


def get_num(text, leave_it_as_it_is = False):
    if leave_it_as_it_is:
        num = input(text)
    else:
        print(text.strip(":"))
        num = input("\n\t: ")

    while num.isnumeric() is False:
        print("\"", num, "\"", " isn't a number. Please enter a number.\n", sep="")
        if leave_it_as_it_is:
            num = input(text)
        else:
            print(text.strip(":"))
            num = input("\n\t: ")

    return int(num)


def get_response(text, max_length = 1000, leave_it_as_it_is = False):
    if leave_it_as_it_is:
        response = input(text)[:max_length]
    else:
        print(text.strip(":"))
        response = input("\n\t: ")[:max_length]

    while response.isalpha() is False:
        print("\"", response, "\"", " isn't comprized of only alphabetical characters.\n", sep="")
        if leave_it_as_it_is:
            response = input(text)[:max_length]
        else:
            print(text.strip(":"))
            response = input("\n\t: ")[:max_length]
    
    return response


def get_y_or_n(text, leave_it_as_it_is = False):
    if leave_it_as_it_is:
        char = get_response(text, 1, True)
    else:
        char = get_response(text, 1)

    while char.lower() != "n" and char.lower() != "y":
        print("Enter [y] or [n]\n")
        if leave_it_as_it_is:
            char = get_response(text, 1, True)
        else:
            char = get_response(text, 1)
    
    return char.lower()


def get_starter_pool():
    cich_pool = []
    cich_exi_water = []
    cich_exi_fire = []
    cich_exi_grass = []

    for cich in CICH_EXI:
        if CICH_EXI[cich] == "water":
            if cich != "Durian":
                cich_exi_water.append(cich)
        elif CICH_EXI[cich] == "fire":
            if cich != "Dragon":
                cich_exi_fire.append(cich)
        elif CICH_EXI[cich] == "grass":
            if cich != "Lily":
                cich_exi_grass.append(cich)

    cich_pool.append(random.choice(cich_exi_water))
    cich_pool.append(random.choice(cich_exi_fire))
    cich_pool.append(random.choice(cich_exi_grass))

    return cich_pool
    
    
def get_starter_choice():
    pool = get_starter_pool()
    you_not_sure = True

    while you_not_sure:
        i = 1

        print("\n---Starter choice---\n")

        for cichnamon in pool:
            print("#" + str(i), cichnamon)
            i += 1

        choice = get_num("\nChoose your Cichnamon!! [1-3]\t")

        while choice > 3 or choice < 1:
            print("You need to enter a number between 1 and 3!!")
            choice = get_num("Choose your Cichnamon!!(again)\t")

        cich_choice = pool[choice-1]

        print("\nYou have chosen:", cich_choice, "it's a", CICH_EXI[cich_choice], "type!")

        if get_y_or_n("\nAre you sure you want to choose " + cich_choice + "? [y][n]\t") == "y":
            you_not_sure = False
        else:
            you_not_sure = True
    
    return cich_choice


def create_cichnamon(cichnamon, name, level = 5, xp = 0, hp = None):
    if cichnamon == "Melon":
        return Melon(name, level, xp, hp)
    elif cichnamon == "Demon":
        return Demon(name, level, xp, hp)
    elif cichnamon == "Rose":
        return Rose(name, level, xp, hp)
    elif cichnamon == "Plum":
        return Plum(name, level, xp, hp)
    elif cichnamon == "Gekko":
        return Gekko(name, level, xp, hp)
    elif cichnamon == "Poppy":
        return Poppy(name, level, xp, hp)
    elif cichnamon == "Kiwi":
        return Kiwi(name, level, xp, hp)
    elif cichnamon == "Chameleon":
        return Chameleon(name, level, xp, hp)
    elif cichnamon == "Dandelion":
        return Dandelion(name, level, xp, hp)
    elif cichnamon == "Durian":
        return Durian(name, level, xp, hp)
    elif cichnamon == "Dragon":
        return Dragon(name, level, xp, hp)
    elif cichnamon == "Lily":
        return Lily(name, level, xp, hp)
    else:
        print("~~~~there is a problem in def create cichnamon~~~~")


def tutorial():
    print("\n---A brief tutorial here---\n")
    print("This game is for 2 or more players.")
    print("If you see ... in the terminal, press enter to continue.")
    print("\nCreate Trainers")
    print("  - Choose the number of players by creating that many trainers.")
    print("  - Made a mistake? You can add more trainers later or use dummy ones.")

    print("\nPick a Starter")
    print("  - Each trainer chooses from 3 randomly selected Cichnamon.")
    print("  - Give your Cichnamon a name (max 20 characters).")

    print("\nGame Options:")
    print("  #0 Save")
    print("\t- Just saves everything. Doesn't end the game.")
    print("  #1 Fight")
    print("\t- Choose 2 trainers to battle.")
    print("\t- Use attacks, whith limited charges and type advantages.")
    print("\t- Attacks can miss or crit.")
    print("\t- You can also defend, switch, or run away.")
    print("\t- Winners earn $300 (or $450 if the opponent chooses to run away).")

    print("  #2 Cichcenter")
    print("\t- Restore HP and move charges of your Cichnamon, or not, if you dare.")
    print("\t- Contains Cichnamon, which you could carry with you.")
    print("\t- You can also put Cichnamon inside and take them out as well.")

    print("  #3 Venture into the wilds")
    print("\t- Explore with friends for a chance to find Cichnamon.")

    print("  #4 Show trainer statistics")
    print("\t- View your stats and Cichnamon details.")

    print("  #5 Create a trainer")
    print("\t- Add a new trainer anytime.")

    print("  #6 Save and exit")
    print("\t- Save your progress and exit the game.")
    
    print("\nFor a more detailed tutorial check the readme.txt that came with this py file")
    print("That's all you need to know. Have fun!")

    print("\n-------------------------------\n\n")


def trainer_create(create_one_trainer = False):
    if create_one_trainer:
        i = len(trainers)

        print("\n---Trainer", i+1, "creation---")
        Trainer(get_response("Write a name for the trainer:\t"))

        trainers[i].add_cichnamon(create_cichnamon(get_starter_choice(), get_response("Enter the name for your Cichnamon:(max length is 20 char)\n\t: ", 20, leave_it_as_it_is= True)))
        print()
        trainers[i].show_stats(True)
    else:
        print("---Trainer creation---")
        num_trainers = get_num("How many trainers do you wanna create?\t")

        while num_trainers < 2:
            num_trainers = get_num("How many trainers do you wanna create?(needs to be more than 1)\t")

        for i in range(num_trainers):
            print("\n---Trainer", i+1, "creation---")
            Trainer(get_response("Write a name for the trainer:\t"))

            trainers[i].add_cichnamon(create_cichnamon(get_starter_choice(), get_response("Enter the name for your Cichnamon:(max length is 20 char)\n\t: ", 20, leave_it_as_it_is= True)))
            print()
            trainers[i].show_stats(True)


def trainer_import():
    print("\n\t---Trainer importation---")
    settings = glob.glob("*_settings.json")
    if len(settings) > 0:
        print("\n---Quick import---")

        num_trainers = 0
        print("Do you want to import: ", end="")
        i = 1
        for string in settings:
            if i == len(settings):
                print(string.split("_")[0], end="")
            elif i + 1 == len(settings):
                print(string.split("_")[0], end=" and ")
            else:
                print(string.split("_")[0], end=", ")
            i += 1
        print("? [y][n]", end="")

        if get_y_or_n("\t") == "y":
            for i in range(len(settings)):
                num_trainers += 1
                name = settings[i].split("_")[0]
                Trainer(name)

                if trainers[i].load_trainer():
                    print()
                    trainers[i].show_stats(True)
                else:
                    print(trainers)
                    return False

            return num_trainers
    else:
        print("\n~~~")
        print("Import canceled!!")
        print("No save files found!!")
        print("~~~\n")
        return False
    
    print("Quick import canceled!!")
    print("\n\n---Regular import---")
    num_trainers = get_num("How many trainers do you wanna import?\t")
    while num_trainers < 1:
        num_trainers = get_num("How many trainers do you wanna import?[needs to be more than 1]\t")
    for i in range(num_trainers):
        print("\n---Trainer", i+1, "importation---")
        Trainer(get_response("What is the name of trainer" + " #" + str(i+1) + "?\t"))
        if trainers[i].load_trainer():
            print()
            trainers[i].show_stats(True)
        else:
            return False
    return num_trainers


def initialize():
    played = get_y_or_n("Have you played before? [y][n]\t").lower()
        
    if played != "y":
        tutorial()
        trainer_create()
        return "created"
    else:
        num_trainers = trainer_import()

        if num_trainers is False:
            return False
        
        if num_trainers < 2:
            print("You can't play alone!")

            trainer_create(create_one_trainer=True)

        return "imported"
    

def print_trainer_names(defined_trainer_names = False):
    trainer_names = []
    if defined_trainer_names is False:
        for trainer in trainers:
            trainer_names.append(trainer.name)
    else:
        for name in defined_trainer_names:
            trainer_names.append(name)

    if len(trainer_names) == 1:
        print("[" + trainer_names[0] + "]")
        return trainer_names
    
    for i in range(len(trainer_names)):
            if i == len(trainer_names) - 1:
                print(trainer_names[i], end="]\n")
            elif i == 0:
                print("[" + trainer_names[i], end=", ")
            else:
                print(trainer_names[i], end=", ")
    
    return trainer_names
    
    
def fight_ini(print_it = False):
    f1_exist = False
    f2_exist = False

    if print_it:
        print("Choose your fighters", end=" ")
        trainer_names = print_trainer_names()

    while f1_exist is False:
        fighter1_name = get_response("Enter the name of trainer #1:\t")
        for trainer in trainers:
            if trainer.name.lower() == fighter1_name.lower():
                fighter1 = trainer
                f1_exist = True
                trainer_names.remove(trainer.name)
                break
        
        if f1_exist is False:
            print("\"" + fighter1_name + "\"", "is not in trainers![there is a mistake in the name]")
            print("\nAvailable trainers are", end=" ")
            print_trainer_names()

    while f2_exist is False:
        fighter2_name = get_response("Enter the name of trainer #2:\t")
        for trainer in trainers:
            if trainer.name.lower() == fighter2_name.lower():
                fighter2 = trainer
                f2_exist = True
                break
        
        if f2_exist is False:
            print("\"" + fighter2_name + "\"", "is not in trainers![there is a mistake in the name]")
            print("\nAvailable trainers are", end=" ")
            print_trainer_names(trainer_names)

    fighter1.fight(fighter2)


def go_cichcenter():
    print("Welcome to Cichcenter!!")

    for trainer in trainers:
        print("\n" + trainer.name + ", what do you want to do here?")

        print("\t[1]Restore Cichnamon")
        print("\t[2]Open cichbox")
        print("\t[3]Restore and open cichbox")

        center_choice = get_num("\nChoose:\t", True)

        if center_choice == 1:
            trainer.owned_cichnamon_restoration()
        elif center_choice == 2:
            go_back = trainer.cichbox_move()
            while go_back:
                go_back = trainer.cichbox_move(False)
        elif center_choice == 3:
            trainer.owned_cichnamon_restoration()

            go_back = trainer.cichbox_move()
            while go_back:
                go_back = trainer.cichbox_move(False)
     

def find_cichnamon():
    find_texts = [
        ", while going through some tall grass you've found", 
        ", while just goofing around a cichnamon showed up,",
        ", during your thorough search for Cichnamon, you've actually found",
        ", without even trying you've stumbled into"
    ]
    end_texts = [
        "And so here comes the decision...",
        "And with that you come back from the wilds and have to make the hard decision...",
        "You continue out of the wilderness, after which there's the difficult choice...",
        "As your venture into the wilds comes to an end, you get to make a choice..."
    ]
    did_find = []
    print("You collectively ventured into the wild.\n")

    for trainer in trainers:
        if random.random() <= 0.8:
            cich_pool = list(CICH_EXI.keys())
            cich = choice(cich_pool, 1, replace = False, p = [1/10, 1/10, 1/10, 1/10, 1/10, 1/10, 1/10, 1/10, 1/10, 1/30, 1/30, 1/30])
            cich = cich[0] #because cich is created as a numpy.array
            trainer_lvl = trainer.get_average_cichnamon_lvl()
            lvl_range = [trainer_lvl - 1, trainer_lvl, trainer_lvl + 1, trainer_lvl + 2]

            wild_cichnamon = create_cichnamon(cich, cich, random.choice(lvl_range))

            print(trainer.name + random.choice(find_texts), wild_cichnamon.name + "!")

            defeated = trainer.wild_fight(wild_cichnamon)
            print()

            if defeated and random.random() <= 0.2:
                print("\nYou've got the chance to keep wild", wild_cichnamon.name + "!")

                print("It's a", wild_cichnamon.type, "type!")

                keep = get_y_or_n(trainer.name + ", do you want to keep " + wild_cichnamon.name + "?" + " [y][n]\t")

                if keep == "y":
                    name = get_response("What do you want to name your newly found cichnamon?[max length is 20 char]\t", 20)
                    trainer.add_cichnamon(create_cichnamon(wild_cichnamon.name, name, wild_cichnamon.lvl, wild_cichnamon.xp))
                    print()
                did_find.append("yes")
            elif defeated:
                did_find.append("no")

                print("But you weren't able to catch the fainted cichnamon!\n")
            else:
                did_find.append("no")
        else:
            defeated = False
            
            print("But", trainer.name, "doesn't find any Cichnamon.")
            input("...")
            print()
            did_find.append("no")

    if did_find[-1] == "no":
        print("\n" + random.choice(end_texts))
    else:
        print(random.choice(end_texts))



def show_trainer_stats():
    name_exi = False

    while name_exi is False:
        print("\nWrite the name of a trainer to show statistics for", end=" ")
        print_trainer_names()           
        trainer_name = get_response("\n\tChoose: ",leave_it_as_it_is = True)

        for trainer in trainers:
            if trainer_name[0].upper() + trainer_name[1:].lower() == trainer.name:
                name_exi = True
                print()
                trainer.show_stats(True)
                break
        
        if name_exi is False:
            print("\"" + trainer_name + "\"", "is not in trainers![there is a mistake in the name]")
            continue
            
        show_cichnamon = get_y_or_n("Show more stats for each cichnamon? [y][n]\t")

        if show_cichnamon == "y":
            print()
            for cichnamon in trainer.owned_cichnamon:
                cichnamon.show_stats(show_advanced = True, show_move_set = True, show_cichclass = True)
                input("...")
                print() 
            
        
        
def whats_next(ini = False):
    if ini is False:
        print("\nWhat do you want to do next?")
    print("\t[0]Save")
    print("\t[1]Fight")
    print("\t[2]Go to a cichcenter (Cichnamon restoration and cichbox)")
    print("\t[3]Venture into the wild to try and find a Cichnamon")
    print("\t[4]Show statistics and Cichnamon of a trainer")
    print("\t[5]Create an additional trainer")
    print("\t[6]Save and exit")

    next_up = get_num("\nChoose:\t", True)
    while next_up < 0 or next_up > 6:
        next_up = get_num("\nChoose(again):\t ", True)
    
    if next_up == 0:
        for trainer in trainers:
            trainer.save_trainer()
        print("\nAll saved, so you don't need to worry about loosing progress!!\n")
    elif next_up == 1:
        fight_ini(True)
    elif next_up == 2:
        go_cichcenter()
    elif next_up == 3:
        find_cichnamon()
    elif next_up == 4:
        show_trainer_stats()
    elif next_up == 5:
        trainer_create(True)
    elif next_up == 6:
        print("Thx for playing my game!!")
    else:
        print("~~~~There is a problem in def whats next~~~~")

    if next_up != 6:
        return True
    else:
        return False

    
def game():
    done = initialize()
    while done is False:
        done = initialize()
    print("Now that you've", done, "your trainers, what do you want to do?")

    go_again = whats_next(True)

    while go_again:
        go_again = whats_next()

    for trainer in trainers:
        trainer.save_trainer()
    
       

print()
print()

#creating moves
water_gun = Move("water-gun", "water", 20, True, 4)
water_slap = Move("water-slap", "water", 20, False, 4)
tackle = Move("tackle", "normal", 20, False, 4)
leaf_shuriken = Move("leaf-shuriken", "grass", 20, True, 4)
fire_fist = Move("fire-fist", "fire", 20, False, 4)
thorns = Move("thorns", "grass", 4, False, 5, 1, 0.06)
roll = Move("roll", "normal", 15, False, 3.5, 1, 0.03)
mini_vortex = Move("mini-vortex", "water", 20, True, 4)
fireball = Move("fireball", "fire", 15, True, 5, 0.7, 0.05)
burning_lick = Move("burning-lick", "fire", 20, False, 4)
whip = Move("whip", "normal", 20, False, 4, 0.8, 0.06)
seed_bombs = Move("seed-bombs", "grass", 10, True, 6, 0.5, 0.01)
bite = Move("bite", "normal", damage=5, accuracy= 0.9)
touch_of_beauty = Move("touch of beauty", "grass", damage=3)
smell_overpower = Move("smell overpower", "water", 8, True, 6, 0.75)
cuteness_overload = Move("cuteness overload", "grass", 10, True, 5, crit_chance=0.05)

game()

#add potions as a class with different functions
#rework moves
#maybe could add trading with cichnamon
#add cichbox loading into trainer_load
#testik

#pouziti gpt na zjednoduseni tutorialu a napsani komandů na jeho vypsani, ktere jsem si potom upravil podle potreb
