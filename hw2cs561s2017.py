import Queue
#from queue import Queue
import copy
import random

que = Queue.Queue()
s = set()
literal_map = {}
friends = []
enemies = []
KB = []
tables = 0
guests = 0


def main():
    """"start the program"""
    try:
        ifile = open('input.txt')
    except:
        return 0

    inputgrid = []
    for line in ifile:
        inputgrid.append(line.strip())

    copy_input_grid(inputgrid)
    covert_to_cnf()
    is_satisfy = pl_resolve(KB)
    if is_satisfy:
        WalkSAT()
    else:
        ofile = open("output.txt", mode='w')
        ofile.write("no")
        ofile.close()


class Literal:
    def __init__(self, person, table, is_negated):
        self.person = person
        self.table = table
        self.is_negated = is_negated

    def __str__(self):
        return "{}, {}, {}".format(self.person, self.table, self.is_negated)

    def __repr__(self):
        return "[{}, {}, {}]".format(self.person, self.table, self.is_negated)

    def is_negated_of(self, l):
        if self.person == l.person and self.table == l.table and self.is_negated != l.is_negated:
            return True
        else:
            return False


def copy_input_grid(inputgrid):
    global tables, guests
    igrid = inputgrid[0].split(' ')
    guests = igrid[0]
    tables = igrid[1]

    for i in range(len(inputgrid) - 1):
        igrid = inputgrid[i + 1].split(' ')
        if igrid[2] == "F":
            friends.append([int(igrid[0]) - 1, int(igrid[1]) - 1])
        else:
            enemies.append([int(igrid[0]) - 1, int(igrid[1]) - 1])


def covert_to_cnf():
    # add Friends conditions
    for f in friends:
        for t in range(int(tables)):
            newfriendclause1 = []
            newfriendclause2 = []

            l1 = Literal(f[0], t, True)
            l2 = Literal(f[0], t, False)
            l3 = Literal(f[1], t, True)
            l4 = Literal(f[1], t, False)

            newfriendclause1.append(l1)
            newfriendclause1.append(l4)
            newfriendclause2.append(l2)
            newfriendclause2.append(l3)

            for i in newfriendclause1:
                literal_map.setdefault(str(i), []).append(newfriendclause1)
            for i in newfriendclause2:
                literal_map.setdefault(str(i), []).append(newfriendclause2)

            KB.append(newfriendclause1)
            KB.append(newfriendclause2)

    # add Enemies coditions
    for e in enemies:
        for t in range(int(tables)):
            newenemyclause1 = []

            l1 = Literal(e[0], t, True)
            l2 = Literal(e[1], t, True)
            newenemyclause1.append(l1)
            newenemyclause1.append(l2)

            for i in newenemyclause1:
                literal_map.setdefault(str(i), []).append(newenemyclause1)
            KB.append(newenemyclause1)

    # add one guest only at one table condition
    for g in range(int(guests)):
        personatleastonetable = []
        for t in range(int(tables)):
            l1 = Literal(g, t, False)
            personatleastonetable.append(l1)

        for m in personatleastonetable:
            literal_map.setdefault(str(m), []).append(personatleastonetable)
        KB.append(personatleastonetable)

        for i in range(int(tables) - 1):
            for j in range(i + 1, int(tables)):
                personatmaxonetable = []
                l1 = Literal(g, i, True)
                l2 = Literal(g, j, True)
                personatmaxonetable.append(l1)
                personatmaxonetable.append(l2)

                for k in personatmaxonetable:
                    literal_map.setdefault(str(k), []).append(personatmaxonetable)
                KB.append(personatmaxonetable)


def pl_resolve(PKB):
    LKB = PKB

    for i in LKB:
        que.put(i)
        st = set()
        for j in i:
            st.add(str(j))
        stemp = sorted(st)
        strr = ""
        strr = ", ".join(str(e) for e in stemp)
        s.add(strr)

    while not que.empty():
        l1 = que.get()
        for i in range(len(l1)):
            line_new = str(l1[i]).split(' ')
            nvalue = line_new[0] + " " + line_new[1] + " " + str(False if line_new[2] == str("True") else True)

            for j in literal_map[nvalue]:
                resolved = resolve(l1, j)
                if que.qsize() > 100001:
                    return True
                if resolved == False:
                    return False
    return True


def resolve(l1, l2):
    temp = []
    ncount = 0
    l1r, l2r = [], []
    for i in range(len(l1)):
        for j in range(len(l2)):
            if l1[i].is_negated_of(l2[j]):
                l1r.append(i)
                l2r.append(j)
                ncount += 1

    all_compliment = ncount == len(l1) == len(l2)
    only_one = ncount == len(l1) == len(l2) == 1
    for i in range(len(l1)):
        if not all_compliment and not l1r.__contains__(i):
            temp.append(l1[i])

    for j in range(len(l2)):
        if not all_compliment and not l2r.__contains__(j):
            temp.append(l2[j])

    if all_compliment and only_one:
        return False
    elif all_compliment:
        return True

    if len(temp) == 0:
        return False

    st = set()
    for j in temp:
        st.add(str(j))
    stemp = sorted(st)
    strr = ""
    strr = ", ".join(str(e) for e in stemp)

    if s.__contains__(strr) == False:
        s.add(strr)
        que.put(temp)
        for i in st:
            literal_map.setdefault(str(i), []).append(temp)


def WalkSAT():
    outfile = open("output.txt", mode='w')
    outfile.write("yes")
    friend_map = {}
    enemy_map = {}
    final_map = {}
    for fri in friends:
        friend_map.setdefault(fri[0], []).append(fri[1])

    for eny in enemies:
        enemy_map.setdefault(eny[0], []).append(eny[1])
        enemy_map.setdefault(eny[1], []).append(eny[0])

    people_map = {}
    for gue in range(int(guests)):
        people_map.setdefault(gue, False)

    def friends_of(f, flist):
        flist.append(f)
        people_map[f] = True
        if friend_map.__contains__(f):
            for fi in friend_map[f]:
                friends_of(fi, flist)

    for t in range(int(tables)):
        for fmap in friend_map:
            if False == people_map[fmap]:
                flist = []
                friends_of(fmap, flist)
                final_map.setdefault(t, flist)
                t += 1

    original_map = copy.deepcopy(final_map)

    if len(final_map) > int(tables):
        for i in range(len(final_map)-1, 0, -1):
            bre = False
            if final_map.__contains__(i):
                for j in final_map[i]:
                    if bre: break
                    if final_map.__contains__(i-1):
                        for k in final_map[i-1]:
                            if enemy_map.__contains__(j):
                                if enemy_map[j][0] == k:
                                    bre = True
                                    break

                if bre == False:
                    temp = final_map[i]
                    temp1 = final_map[i-1]
                    final_map[i-1] = temp + temp1
                    del final_map[i]

    t, g, j = 0, 0, 0
    for g in range(int(guests)):
        if people_map[g] == False:
            if enemy_map.__contains__(g):
                for t in range(int(tables)):
                    if len(final_map) == 0:
                        final_map.setdefault(t, []).append(g)
                        people_map[g] = True
                        for p in enemy_map[g]:
                            final_map.setdefault(t+1, []).append(p)
                            people_map[p] = True
                        break
                    else:
                        list = final_map[t]
                        l = 0
                        enemy_exists = False
                        for l in list:
                            if enemy_exists == True:
                                break
                            for e in enemy_map[g]:
                                if e == l:
                                    enemy_exists = True
                                    break
                        people_map[g] = True
                        if enemy_exists == False:
                            final_map.setdefault(t, []).append(g)
                        elif t > 0:
                            final_map.setdefault(t-1, []).append(g)
                        else:
                            final_map.setdefault(t+1, []).append(g)
                        break
            else:
                final_map.setdefault(t, []).append(g)
                people_map[g] = True

    if len(final_map) > int(tables):
        def check_enemy(a, b):
            for p in a:
                for q in b:
                    if enemy_map.__contains__(p):
                        for e in enemy_map[p]:
                            if q == e:
                                return True
            return False

        final_map = original_map
        satisfied = False
        table_assign = []
        key_of = []
        for key1 in final_map:
            table_assign.append(0)
            key_of.append(key1)

        for i in range(0, 10000):
            if(satisfied):
                break
            else:
                enemy_count = 0
                for i1 in range(0, len(final_map)):
                    for i2 in range(0, len(final_map)):
                        if i1 != i2 and table_assign[i1] == table_assign[i2]:
                            if check_enemy(final_map[key_of[i1]], final_map[key_of[i2]]):
                                enemy_count+=1
                                if random.randint(0,1) == 0:
                                    table_assign[i1] = random.randint(0, int(tables)-1)
                                    break
                                else:
                                    table_assign[i2] = random.randint(0, int(tables) - 1)
                                    break
                    if enemy_count != 0:
                        break
                if enemy_count == 0:
                    satisfied = True

        final_map = {}
        for i in range(0, len(table_assign)):
            final_map.setdefault(table_assign[i], [])
            for val in original_map[key_of[i]]:
                final_map.setdefault(table_assign[i], []).append(val)

    stri = ""
    arra = []
    for r in range(int(guests)+1):
        arra.append(-1)
    for fm in final_map:
        for z in final_map[fm]:
            arra[z+1]=fm+1

    for q in range(1,int(guests)+1,1):
        stri = "\n"+str(q)+" "+str(arra[q])
        outfile.write(stri)
    outfile.close()


if __name__ == "__main__": main()
