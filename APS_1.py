#Definindo operadores lógicos da mic-1:

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

#Uma função auxiliar da ula que recebe A e B com 32 bits:
def aux_ULA(lista_A, lista_B, f0, f1, enA, enB, invA, inc):
    saida_final = [0] * 32
    
    #O sinal inc (0 ou 1) entra como o primeiro carry na posição mais à direita
    carry_atual = inc  

    for i in range(31, -1, -1):
        #Pega o bit individual atual de cada vetor
        bit_A = lista_A[i]
        bit_B = lista_B[i]
        
        #Faz cada bit de a e b entrar na lógica da ULA
        resultado_vai_um, resultado_saida = ULA(bit_A, bit_B, f0, f1, enA, enB, invA, carry_atual)
        
        #Guarda o bit gerado na posição correspondente da saída
        saida_final[i] = resultado_saida
        
        #Caso a IR determine uma soma de bits, precisamos passar o vai-um de uma iteração para a próxima iteração
        if f0 == 1 and f1 == 1:
            carry_atual = resultado_vai_um
        else:
            carry_atual = 0

    #Ao final das 32 iterações, o último carry_atual gerado na posição 0 é o Carry-out (co)
    co_final = carry_atual
    
    return saida_final, co_final

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

    return or2, or3

def main():
    #Criando b e a:
    b = []
    while len(b) != 31:
        b.append(0)
    b.append(1)
    a = []
    while len(a) != 32:
        a.append(1)
    
    pc = 1
    ir = [0] * 6

    #Criando log e lendo arquivo de textes:
    with open('log.txt', 'w', encoding='utf-8') as log:
        log.write(f"b = {b}\n")
        log.write(f"a = {a}\n")
        log.write("\n")
        log.write("Start of program\n")

        #Lendo texte que a professora disponibilizou como base
        with open('teste.txt', 'r') as read:
            for instrucao in read:

                #ignora linhas vazias:
                if not instrucao.strip():
                    continue

                #Montando a instrução para ser lida pela ULA
                i = 0
                for h in instrucao.strip():
                    if h == '0':
                        ir[i] = 0
                        i+=1
                    elif h == '1':
                        ir[i] = 1
                        i+=1

                #Verificando ENA e ENB:
                a_exibido = []
                b_exibido = []
                
                #Caso 1, deixa os bits do mesmo jeito
                if (ir[2] == 1):
                    a_exibido = a

                #Caso 0, zera os 32 bits
                elif (ir[2] == 0):
                    a_exibido = [0] * 32
                
                #O mesmo para b:
                if (ir[3] == 1):
                    b_exibido = b
                elif (ir[3] == 0):
                    b_exibido = [0] * 32
                
                #Armazenando resultado e soma de A e B
                s, vaiUm = aux_ULA(a_exibido,b_exibido, ir[0], ir[1], ir[2], ir[3], ir[4], ir[5])

                #Escrevendo no log:
                escritor = ["====================\n", f"Cycle {pc}\n", "\n", f"PC = {pc}\n", f"IR = {ir}\n", f"b = {b_exibido}\n", f"a = {a_exibido}\n", f"s = {s}\n", f"co = {vaiUm}\n"]
                
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