import copy

#Funções úteis:
def junta_bits(lista_bits):
    # Transforma cada inteiro da lista em string e junta todos sem espaços
    return "".join(map(str, lista_bits))

#Função auxiliar para pegar os 4 bits mais a direita e retornar o o nome do registrador para impressão:
def get_reg(bits):
                
                #Dicionário para mapear os 4 bits para um registrador
                mapeamento_b = {
                                "0000": "mdr",
                                "0001": "pc",
                                "0010": "mbr",
                                "0011": "mbru",
                                "0100": "sp",
                                "0101": "lv",
                                "0110": "cpp",
                                "0111": "opc",  
                                "1000": "tos"   
                            }
                
                #Formatando a lista de bits recebida para uma string 
                bits_b_formatado = "".join(map(str, bits))

                #Tentando achar registrador corrpespondente:
                reg_b = mapeamento_b.get(bits_b_formatado, "nenhum")
    
                return reg_b

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

#Função para carregar os valores dos registradores no nosso programa:
def inicializar_registradores(caminho):
    #Criando dicionário para armazenar registradores:
    registradores = {
        "mar": [0]*32,
        "mdr": [0]*32,
        "pc":  [0]*32,
        "mbr": [0]*8,
        "sp":  [0]*32,
        "lv":  [0]*32,
        "cpp": [0]*32,
        "tos": [0]*32,
        "opc": [0]*32,
        "h":   [0]*32
    }

    with open(caminho, 'r', encoding= 'utf-8') as file:
        for linha in file:
            #Tirando espaços em branco
            linha = linha.strip()

            #Pulando linhas em branco:
            if not linha:
                continue
            
            #Separando registrador e valor em duas variáveis:
            r, valor = linha.split(' = ')

            #Convertendo valor em uma lista para guardar no dicionário:
            valor_listado = inicializa_entrada(valor)

            #Tratando o nome de r para não dar erro:
            r = r.lower()

            #Inserindo valor do registrador no dicionário:
            registradores[r] = valor_listado
    
    return registradores

#Função para pegar entradas no formato de strings e transformar em uma lista de inteiros
def inicializa_entrada(entrada):
    #Pega o tamnho da string pra usar como base na lista
    tamanho = len(entrada)


    entrada_inicializada = [0] * tamanho
    
    #Preenche a lista com os respectivos números
    for i in range(0,tamanho):
        if entrada[i] == '0':
            entrada_inicializada[i] = 0
        elif entrada[i] == '1':
            entrada_inicializada[i] = 1
        
    return entrada_inicializada

#Função para ativar registradior no barramento B:
def ativa_registrador_b(reg, bits):
    #convertendo em decimal:
    decimal = int("".join(map(str, bits)), 2)

    # Mapeamento direto dos registradores de 32 bits (Seguindo a documentação do projeto):

    if decimal == 0:
        return reg["mdr"]
    
    elif decimal == 1:
        return reg["pc"]
    
    elif decimal == 2:
        #Realizar conversão para 32 bits:
        preenchimento = [0] * 24
        return (preenchimento + reg["mbr"])
    
    elif decimal == 3:
        #Realizar conversão para 32 bits:
        bit_sinal = reg["mbr"][0]
        sinal_repetido = [bit_sinal] * 24

        return (sinal_repetido + reg["mbr"])
    
    elif decimal == 4:
        return reg["tos"]
    
    elif decimal == 5:
        return reg["cpp"]
    
    elif decimal == 6:
        return reg["lv"]
    
    elif decimal == 7:
        return reg["opc"]
    
    elif decimal == 8:
        return reg["sp"]
    
    else:
        #Vai uma instrução zerada
        return [0] * 32

#Função para escrever o valor de sd nos registradores em específico:
def mapeamento_barramento_c(regs, barramento_c, sd):
    modificados = []

    # Mapeamento direto seguindo a convenção padrão Mic-1 (esquerda para a direita)
    #Caso cada bit esteja alto (1), signifca que o seu respectivo registrador será modificado 
    if barramento_c[0] == 1:
        regs["h"] = sd
        modificados.append("H")
    if barramento_c[1] == 1:
        regs["opc"] = sd
        modificados.append("OPC")
    if barramento_c[2] == 1:
        regs["tos"] = sd
        modificados.append("TOS")
    if barramento_c[3] == 1:
        regs["cpp"] = sd
        modificados.append("CPP")
    if barramento_c[4] == 1:
        regs["lv"] = sd
        modificados.append("LV")
    if barramento_c[5] == 1:
        regs["sp"] = sd
        modificados.append("SP")
    if barramento_c[6] == 1:
        regs["pc"] = sd
        modificados.append("PC")
    if barramento_c[7] == 1:
        regs["mdr"] = sd
        modificados.append("MDR")
    if barramento_c[8] == 1:
        regs["mar"] = sd
        modificados.append("MAR")

    return modificados

def main():
    #Lendo os registradores do txt e inicializando-os no programa:
    registradores = inicializar_registradores("APS2_Tarefa2/registradores_APS2.txt")
    
    #Inicializando pc e ir:
    pc = 1
    ir = [0] * 21
    
    #Criando log e lendo arquivo txt:
    with open('APS2_Tarefa2/log_Aps2_Tarefa2.txt', 'w', encoding='utf-8') as log:
        log.write("=" * 5 + ":Log gerado para a segunda tarefa da APS 2:" + "=" * 5)
        log.write("\n\nInstruções de 21 bits lidas do arquivo texte.txt:\n")

        # Leitura prévia para listar as instruções no topo do arquivo
        with open('APS2_Tarefa2/teste.txt', 'r') as read_previa:
            for linha in read_previa:
                if linha.strip():
                    log.write(f"{linha.strip()}\n")
        read_previa.close()

        # Estado Inicial dos Registradores
        log.write("==*" * 20)
        log.write("\n> Initial register states\n")
        
        #Exibir nome e valor do registrador:
        for nome_reg, lista_bits in registradores.items():
            log.write(f"{nome_reg} = {junta_bits(lista_bits)}\n")
        
        log.write("==*" * 20)
        log.write("\nStart of program\n")

        #Lendo txt que a professora disponibilizou como base
        with open('APS2_Tarefa2/teste.txt', 'r') as read:
            for instrucao in read:
                #Zerando ir para não causar interferência nas próximas ir's:
                ir = [0] * 21

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
                
                #Realizando fatiamento da ir:
                bits_ir = ir[0:8] #Servirá como o antigo ir
                bits_barramento_c = ir[8:17] 
                bits_barramento_b = ir[17:21] 

                #ativando registrador no barramento b:
                b = ativa_registrador_b(registradores, bits_barramento_b)

                #Ativando valor de a de acordo com o registrador H:
                a = registradores["h"]

                # Criando um dicionário para armazenar o estado dos registradores (antes da instrução)
                regs_antes = regs_antes = copy.deepcopy(registradores)

                # Escrevendo a identificação do Ciclo
                log.write("==*" * 20)
                log.write(f"\nCycle {pc}\n")

                #Verficação de SLL8 e SRA1
                if (bits_ir[0] == 1 and bits_ir[1] == 1):  
                    log.write(f"ir = {junta_bits(bits_ir)} {junta_bits(bits_barramento_c)} {junta_bits(bits_barramento_b)}\n")
                    log.write("> Error, invalid control signals.\n") #SLL8 e SRA1 não podem ter nível lógico alto ao mesmo tempo
                    pc += 1
                    continue

                #Verificando ENA e ENB:
                a_exibido = []
                b_exibido = []
                
                #Caso 1, deixa os bits do mesmo jeito
                if (bits_ir[4] == 1):
                    a_exibido = a

                #Caso 0, zera os 32 bits
                elif (bits_ir[4] == 0):
                    a_exibido = [0] * 32
                
                #O mesmo para b:
                if (bits_ir[5] == 1):
                    b_exibido = b
                elif (bits_ir[5] == 0):
                    b_exibido = [0] * 32
                
                #Armazenando resultado deslocado
                _, sd, _, _, _ = aux_ULA(a_exibido, b_exibido, bits_ir[0], bits_ir[1], bits_ir[2], bits_ir[3], bits_ir[4], bits_ir[5], bits_ir[6], bits_ir[7])

                #Mapeando os bits do barramento C para determinar quais registradores devem ser reescritos:
                registradores_atualizados = mapeamento_barramento_c(registradores, bits_barramento_c, sd)

                # Exibindo IR de 21 bits:
                log.write(f"ir = {junta_bits(bits_ir)} {junta_bits(bits_barramento_c)} {junta_bits(bits_barramento_b)}\n")

                # Descobre o nome do registrador para o log do b_bus
                reg_b = get_reg(bits_barramento_b)
                log.write(f"b_bus = {reg_b}\n")
                
                # Formatando a lista do c_bus
                c_bus_formatado = ", ".join(registradores_atualizados).lower()
                log.write(f"c_bus = {c_bus_formatado}\n\n")

                # Printando o estado dos registradores antes da instrução
                log.write("> Registers before instruction\n")
                for nome_reg, lista_bits in regs_antes.items():
                    log.write(f"{nome_reg} = {junta_bits(lista_bits)}\n")
                
                log.write("\n")

                # Printando o estado dos registradores depois da instrução
                log.write("> Registers after instruction\n")
                for nome_reg, lista_bits in registradores.items():
                    log.write(f"{nome_reg} = {junta_bits(lista_bits)}\n")

                # Avança para o próximo ciclo de clock
                pc += 1
        
        read.close()

        #Exibe no log que não tem mais nada a ser lido:
        log.write("==*" * 20)
        log.write(f"\nCycle {pc}\n")
        log.write("\n")
        log.write(f"PC = {pc}\n")
        log.write("> Line is empty, EOP.\n")
    
    log.close()

main()