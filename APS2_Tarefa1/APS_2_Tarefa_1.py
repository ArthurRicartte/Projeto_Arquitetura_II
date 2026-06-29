#Funções úteis:
def junta_bits(lista_bits):
    # Transforma cada inteiro da lista em string e junta todos sem espaços
    return "".join(map(str, lista_bits))

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

#Função que verifica os bits da saída da ULA para determinar o campo Z:
def define_Z(saida_ULA):
    #Para z ser 1, todos os 32 bits precisam ser 0
    for i in range(0,32):
        if (saida_ULA[i] == 1):
            return 0
    
    return 1

#Função que verifica os bits da saída da ULA para determinar o campo N:
def define_N(f0, f1, co):
    #Caso f0 e f1 indiquem uma operação de soma, N é igual ao co, caso contrário, é igual a 0
    if (f0 == 1 and f1 == 1):
        return co

    return 0

#Função que calcula descolamento à esquerda de 8 bits:
def desloca_esquerda_logico (soma):
    saida_deslocada = [0] * 32

    #Deslocando a saída 8 bits à esquerda:
    for i in range(0, 24):
        saida_deslocada[i] = soma[i + 8]

    #Retornando saída com deslocamento de 8 bits:
    return saida_deslocada

#Função que calcula deslocamento aritmético de 1 bit à direita:
def desloca_direita_aritmetico (soma):
    saida_deslocada = [0] * 32

    #Duplicando primeiro bit da sequência (por ser uma soma aritmética, duplicamos o primeiro bit)
    saida_deslocada[0] = soma[0]
    for i in range(1, 32):
        #realizando deslocamento:
        saida_deslocada[i] = soma[i - 1] 

    #Retornando saída da ULA deslocada 1 bit à direita:
    return saida_deslocada

#Uma função auxiliar da ula que recebe A e B com 32 bits:
def aux_ULA(lista_A, lista_B, sll8, sra1, f0, f1, enA, enB, invA, inc):
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

    #Verifca os campos sll8, sra1:
    saida_deslocada = [0] * 32
    if (sll8 == 1):
        saida_deslocada = desloca_esquerda_logico(saida_final)
    elif(sra1 == 1):
        saida_deslocada = desloca_direita_aritmetico(saida_final)
    else:
        saida_deslocada = saida_final
    
    #Determinando N e Z:

    #Para Z, basta analisar se existe algum bit da saída que seja 1:
    z = define_Z(saida_final)

    #Para N, basta analisar f0, f1 e co_final:
    n = define_N(f0, f1, co_final)
    
    return saida_final, saida_deslocada, n, z, co_final

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


#Função para pegar entradas no formato de strings e transformar em uma lista de inteiros
def inicializa_entrada(entrada):
    entrada_inicializada = [0] * 32
    for i in range(0,32):
        if entrada[i] == '0':
            entrada_inicializada[i] = 0
        elif entrada[i] == '1':
            entrada_inicializada[i] = 1
        
    return entrada_inicializada

def main():
    '''Criando b e a (De acordo com o log disponibilizado pela professora):
       Provavelmente na hora de apresentar a professora vai gerar uma chave pra A e B, 
       então, fiz essa função pra não perder tempo criando e inserindo bit a bit na lista
       só copiar e colar no parâmentro da função
     '''

    b = inicializa_entrada("10000000000000000000000000000000")
    a = inicializa_entrada("00000000000000000000000000000001") 
   
    #Inicializando pc e ir:
    pc = 1
    ir = [0] * 8
    
    #Criando log e lendo arquivo de textes:
    with open('APS2_Tarefa1/log_Aps2_Tarefa1.txt', 'w', encoding='utf-8') as log:
        log.write(f"b = {junta_bits(b)}\n")
        log.write(f"a = {junta_bits(a)}\n")
        log.write("\n")
        log.write("Start of program\n")

        #Lendo texte que a professora disponibilizou como base
        with open('APS2_Tarefa1/teste.txt', 'r') as read:
            for instrucao in read:
                #Zerando ir para não causar interferência nas próximas ir's:
                ir = [0] * 8

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
                
                #Escrevendo cabeçalho:
                log.write("=====================" * 4)
                log.write(f"\nCycle {pc}\n")
                log.write("\n")
                log.write(f"PC = {pc}\n")

                #Verficação de SLL8 e SRA1
                if (ir[0] == 1 and ir[1] == 1):  
                    log.write(f"IR = {junta_bits(ir)}\n")
                    log.write("> Error, invalid control signals.\n") #SLL8 e SRA1 não podem ter nível lógico alto ao mesmo tempo
                    pc += 1
                    continue

                #Verificando ENA e ENB:
                a_exibido = []
                b_exibido = []
                
                #Caso 1, deixa os bits do mesmo jeito
                if (ir[4] == 1):
                    a_exibido = a

                #Caso 0, zera os 32 bits
                elif (ir[4] == 0):
                    a_exibido = [0] * 32
                
                #O mesmo para b:
                if (ir[5] == 1):
                    b_exibido = b
                elif (ir[5] == 0):
                    b_exibido = [0] * 32
                
                #Armazenando resultado, deslocamento, flags e carry out
                s, sd, n, z, vaiUm = aux_ULA(a_exibido, b_exibido, ir[0], ir[1], ir[2], ir[3], ir[4], ir[5], ir[6], ir[7])

                #Escrevendo no log:
                escritor = [
                    f"IR = {junta_bits(ir)}\n", 
                    f"b = {junta_bits(b_exibido)}\n", 
                    f"a = {junta_bits(a_exibido)}\n", 
                    f"s = {junta_bits(s)}\n", 
                    f"sd = {junta_bits(sd)}\n",   
                    f"n = {n}\n", 
                    f"z = {z}\n",
                    f"co = {vaiUm}\n"
                ]
                
                i = 0
                while i < 8:
                    log.write(escritor[i])
                    i+=1

                pc+=1
        
        read.close()

        #Exibe no log que não tem mais nada a ser lido:
        log.write("=====================" * 4)
        log.write(f"\nCycle {pc}\n")
        log.write("\n")
        log.write(f"PC = {pc}\n")
        log.write("> Line is empty, EOP.\n")
    
    log.close()

main()