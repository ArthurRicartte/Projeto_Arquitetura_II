def andLogic(sup, low):
    if sup == 0:
        return 0
    else:
        return low

def orLogic(sup, low):
    if sup == 1:
        return 1
    else:
        return low

def notLogic(sig):
    if sig == 0:
        return 1
    else:
        return 0

def xorLogic(sup, low):
    if sup != low:
        return 1
    else:
        return 0

def complem2(x):
    s = []
    i = 0
    while i < len(x):
        s.append(notLogic(x[i]))

    inc = [0] * 31
    inc.append(1)

    s = somaBin(s, inc)

    print("Valor em complemento de 2")
    return s


def ULA(A, B, f0, f1, enA, enB, invA, inc):
    #entrada superior
    and1 = andLogic(A, enA)
    and2 = andLogic(B, enB)
    xor1 = xorLogic(invA, and1)

    #decodificador
    and3 = andLogic(notLogic(f0), notLogic(f1))
    and4 = andLogic(notLogic(f0), f1)
    and5 = andLogic(f0, notLogic(f1))
    and6 = andLogic(f0, f1)

    #unidade logica
    and7 = andLogic(xor1, and2)
    or1 = orLogic(xor1, and2)
    and8 = andLogic(and7, and3)
    and9 = andLogic(or1, and4)
    and10 = andLogic(notLogic(and2), and5)

    #somador
    opAnd11 = andLogic(xor1, and2)
    and11 = andLogic(opAnd11, and6)
    xor2 = xorLogic(xor1, and2)
    opAnd12 = andLogic(xor2, and6)
    and12 = andLogic(inc, opAnd12)
    or2 = orLogic(and11, and12) #VaiUm
    xor3 = xorLogic(inc, xor2)
    and13 = andLogic(xor3, and6)

    #saida
    opOr3sup = orLogic(and8, and9)
    opOr3low = orLogic(and10, and13)
    or3 = orLogic(opOr3sup, opOr3low) #Saida

    return [or2, or3]

def somaBin(a, b):
    s = [0] * 32
    carry = 0

    for i in range(31, -1, -1):
        soma = a[i] + b[i] + carry

        if soma >= 2:
            s[i] = soma % 2
            carry = 1
        else:
            s[i] = soma
            carry = 0

    if carry == 1:
        print("Overflow de memória, s = 0")
        s = [0] * 32

    return s

def subtraBin(a, b):
    s = [0] * 32
    borrow = 0

    for i in range(31, -1, -1):
        diff = a[i] - b[i] - borrow

        if diff < 0:
            s[i] = diff + 2
            borrow = 1
        else:
            s[i] = diff
            borrow = 0

    if borrow == 1:
        s = complem2(s)

    return s

def operac(b, a, ir):
    s = []
    i = 0
    inc = [0] * 31
    inc.append(1)

    if ir == [0,1,1,0,0,0] or ir == [1,1,1,0,0,0]:
        s = a
    elif ir == [0,1,0,1,0,0] or ir == [1,1,0,1,0,0]:
        s = b
    elif ir == [0,1,1,0,1,0]:
        while i < len(a):
            s.append(notLogic(a[i]))
            i+=1
    elif ir == [1,0,1,1,0,0]:
        while i < len(b):
            s.append(notLogic(b[i]))
            i+=1
    elif ir == [1,1,1,1,0,0]:
        s = somaBin(a, b)
    elif ir == [1,1,1,1,0,1]:
        s = somaBin(a, b)
        s = somaBin(s, inc)
    elif ir == [1,1,1,0,0,1]:
        s = somaBin(a, inc)
    elif ir == [1,1,0,1,0,1]:
        s = somaBin(b, inc)
    elif ir == [1,1,1,1,1,1]:
        s = subtraBin(b, a)
    elif ir == [1,1,0,1,1,0]:
        s = subtraBin(b, inc)
    elif ir == [1,1,1,0,1,1]:
        s = subtraBin(s, a)
    elif ir == [0,0,1,1,0,0]:
        while i < len(b):
            s.append(andLogic(b[i], a[i]))
            i+=1
    elif ir == [0,1,1,1,0,0]:
        while i < len(a):
            s.append(orLogic(b[i], a[i]))
            i+=1
    elif ir == [0,1,0,0,0,0]:
        s = [0] * 32
    elif ir == [1,1,0,0,0,1]:
        s = inc
    elif ir == [1,1,0,0,1,0]:
        s = complem2(inc)
    else:
        print("Instrucao invalida")
        s = [0] * 32

    return s


def main():
    b = []
    while len(b) != 31:
        b.append(0)
    b.append(1)
    a = []
    while len(a) != 32:
        a.append(1)
    
    pc = 1
    ir = [0] * 6

    with open('log.txt', 'w', encoding='utf-8') as log:
        log.write(f"b = {b}\n")
        log.write(f"a = {a}\n")
        log.write("\n")
        log.write("Start of program\n")

        with open('teste.txt', 'r') as read:
            for instrucao in read:
                i = 0
                for h in instrucao:
                    if h == '0':
                        ir[i] = 0
                        i+=1
                    elif h == '1':
                        ir[i] = 1
                        i+=1

                retornoULA = ULA(1, 1, ir[0], ir[1], ir[2], ir[3], ir[4], ir[5])
                sBit = retornoULA[0]
                vaiUm = retornoULA[1]

                s = operac(b, a, ir)

                escritor = ["====================\n", f"Cycle {pc}\n", "\n", f"PC = {pc}\n", f"IR = {ir}\n", f"b = {b}\n", f"a = {a}\n", f"s = {s}\n", f"co = {vaiUm}\n"]
                i = 0
                while i < 9:
                    log.write(escritor[i])
                    i+=1

                pc+=1
        read.close()
        log.write("====================\n")
        log.write(f"Cycle {pc}\n")
        log.write("\n")
        log.write(f"PC = {pc}\n")
        log.write("> Line is empty, EOP.\n")
    log.close()

main()