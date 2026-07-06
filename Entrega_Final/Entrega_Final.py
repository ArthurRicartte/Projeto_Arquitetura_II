import copy
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


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
                return mapeamento_b.get(bits_b_formatado, "nenhum")
    
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

def ULA(A, B, f0, f1, enA, enB, invA, inc):
    # entrada superior
    and1 = andLogic(A, enA)
    and2 = andLogic(B, enB)
    xor1 = xorLogic(invA, and1)

    # decodificador
    and3 = andLogic(notLogic(f0), notLogic(f1))
    and4 = andLogic(notLogic(f0), f1)
    and5 = andLogic(f0, notLogic(f1))
    and6 = andLogic(f0, f1)

    # unidade logica
    and7 = andLogic(xor1, and2)
    or1 = orLogic(xor1, and2)
    and8 = andLogic(and7, and3)
    and9 = andLogic(or1, and4)
    and10 = andLogic(notLogic(and2), and5)

    # somador
    opAnd11 = andLogic(xor1, and2)
    and11 = andLogic(opAnd11, and6)
    xor2 = xorLogic(xor1, and2)
    opAnd12 = andLogic(xor2, and6)
    and12 = andLogic(inc, opAnd12)
    or2 = orLogic(and11, and12)  # VaiUm
    xor3 = xorLogic(inc, xor2)
    and13 = andLogic(xor3, and6)

    # saida
    opOr3sup = orLogic(and8, and9)
    opOr3low = orLogic(and10, and13)
    or3 = orLogic(opOr3sup, opOr3low)

    return or2, or3

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

def ativa_registrador_b(reg, bits):
    decimal = int("".join(map(str, bits)), 2)
    if decimal == 0:
        return reg["mdr"]
    elif decimal == 1:
        return reg["pc"]
    elif decimal == 2:
        return ([0] * 24) + reg["mbr"]        # MBR (8 bits -> 32 bits com zeros à esquerda)
    elif decimal == 3:
        bit_sinal = reg["mbr"][0]
        return ([bit_sinal] * 24) + reg["mbr"] # MBRU (extensão de sinal)
    elif decimal == 4:
        return reg["sp"]
    elif decimal == 5:
        return reg["lv"]
    elif decimal == 6:
        return reg["cpp"]
    elif decimal == 7:
        return reg["opc"]
    elif decimal == 8:
        return reg["tos"]
    else:
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

def carregar_memoria_dados(caminho):
    memoria = []
    with open(caminho, 'r', encoding='utf-8') as f:
        for linha in f:
            linha = linha.strip()
            if linha:
                memoria.append(linha)
    return memoria

def traduzir_instrucoes(caminho_instrucoes):
    microinstrucoes_finais = []
    
    with open(caminho_instrucoes, 'r', encoding='utf-8') as f:
        for linha in f:
            linha = linha.strip()
            if not linha:
                continue
                
            partes = linha.split()
            comando = partes[0].upper()
            
            if comando == "ILOAD":
                x = int(partes[1])
                microinstrucoes_finais.append("00110100100000000000101")     # H = LV
                for _ in range(x):
                    microinstrucoes_finais.append("00111001100000000000000") # H = H + 1
                microinstrucoes_finais.append("00111000000000001010000")     # MAR = H; rd
                microinstrucoes_finais.append("00110101000001001100100")     # MAR = SP = SP + 1; wr
                microinstrucoes_finais.append("00110100001000000000000")     # TOS = MDR
                
            elif comando == "DUP":
                microinstrucoes_finais.append("00110101000001001000100")     # MAR = SP = SP + 1
                microinstrucoes_finais.append("00110100000000010101000")     # MDR = TOS; wr
                
            elif comando == "BIPUSH":
                byte_arg = partes[1]
                microinstrucoes_finais.append("00110101000001001000100")     # SP = MAR = SP + 1
                
                # verificacao de binario ou decimal?
                if len(byte_arg) == 8 and all(c in '01' for c in byte_arg):
                    byte_bin = byte_arg 
                else:
                    byte_val = int(byte_arg)
                    byte_bin = bin(byte_val & 0xff)[2:].zfill(8)
                    
                instrucao_especial = byte_bin + "000000000110000"
                microinstrucoes_finais.append(instrucao_especial)
                
                microinstrucoes_finais.append("00111000001000010100000")     # MDR = TOS = H; wr

    return microinstrucoes_finais

def main():
    # Obtém o diretório onde o script atual está guardado
    diretorio_script = os.path.dirname(os.path.abspath(__file__))

    # Nomes dos txt's
    arq_dados = os.path.join(diretorio_script, "dados.txt")
    arq_regs = os.path.join(diretorio_script, "registradores.txt")
    arq_instrucoes = os.path.join(diretorio_script, "instruções.txt")
    arq_log = os.path.join(diretorio_script, "log.txt")
    
    # Inicializando dados
    memoria_dados = carregar_memoria_dados(arq_dados)
    registradores = inicializar_registradores(arq_regs)
    
    # aplica a função para traduzir os 23 bits para instruções de 32 bits
    instrucoes_23_bits = traduzir_instrucoes(arq_instrucoes)

    with open(arq_log, 'w', encoding='utf-8') as log:
        log.write("=" * 60 + "\nInitial memory state\n" + "*" * 40 + "\n")
        for linha in memoria_dados:
             log.write(linha + "\n")
        log.write("*" * 30 + "\nInitial register state\n" + "*" * 40 + "\n")
        
        ordem_regs = ["mar", "mdr", "pc", "mbr", "sp", "lv", "cpp", "tos", "opc", "h"]
        for nome in ordem_regs: 
            log.write(f"{nome} = {junta_bits(registradores[nome])}\n")
        
        log.write("\n" + "=" * 60 + "\nStart of Program\n" + "=" * 60 + "\n")

        pc = 1
        for instrucao_str in instrucoes_23_bits:
            ir = [int(c) for c in instrucao_str]

            bits_ula = ir[0:8]         
            bits_c   = ir[8:17]        
            bits_mem = ir[17:19]       
            bits_b   = ir[19:23]       

            # opção do BIPUSH que usa read e write nos bits mais significativos na memória simultanemanete
            if bits_mem[0] == 1 and bits_mem[1] == 1:
                byte_arg = bits_ula 
                registradores["mbr"] = byte_arg
                registradores["h"] = ([0] * 24) + byte_arg
                
                log.write(f"Cycle {pc}\n")
                log.write(f"ir = {junta_bits(bits_ula)} {junta_bits(bits_c)} {junta_bits(bits_mem)} {junta_bits(bits_b)}\n")
                log.write("> Special fetch executed (MBR and H updated directly)\n")
                log.write("=" * 60 + "\n")
                pc += 1
                continue

            sll8, sra1, f0, f1, enA, enB, invA, inc = bits_ula

            if sll8 == 1 and sra1 == 1:
                log.write(f"\nCycle {pc}\nir = {junta_bits(bits_ula)} {junta_bits(bits_c)} {junta_bits(bits_mem)} {junta_bits(bits_b)}\n> Error, invalid control signals.\n")
                pc += 1
                continue

            b = ativa_registrador_b(registradores, bits_b)
            a = registradores["h"]

            a_eff = a if enA == 1 else [0] * 32
            b_eff = b if enB == 1 else [0] * 32

            regs_antes = copy.deepcopy(registradores)
            _, sd, _, _, _ = aux_ULA(a_eff, b_eff, sll8, sra1, f0, f1, enA, enB, invA, inc)
            regs_modificados = mapeamento_barramento_c(registradores, bits_c, sd)

            if bits_mem[0] == 1:          
                endereco = int(junta_bits(registradores["mar"]), 2)
                if 0 <= endereco < len(memoria_dados): memoria_dados[endereco] = junta_bits(registradores["mdr"])
            elif bits_mem[1] == 1:        
                endereco = int(junta_bits(registradores["mar"]), 2)
                if 0 <= endereco < len(memoria_dados): registradores["mdr"] = inicializa_entrada(memoria_dados[endereco])

            # ecrita no log
            log.write(f"Cycle {pc}\nir = {junta_bits(bits_ula)} {junta_bits(bits_c)} {junta_bits(bits_mem)} {junta_bits(bits_b)}\n")
            log.write(f"b = {get_reg(bits_b)}\nc = {' '.join([nome.lower() for nome in regs_modificados])}\n")
            
            log.write("\n> Registers before instruction\n" + "*" * 40 + "\n")
            for nome in ordem_regs: log.write(f"{nome} = {junta_bits(regs_antes[nome])}\n")

            log.write("\n> Registers after instruction\n" + "*" * 40 + "\n")
            for nome in ordem_regs: log.write(f"{nome} = {junta_bits(registradores[nome])}\n")

            log.write("\n> Memory after instruction\n" + "*" * 40 + "\n")
            for linha in memoria_dados: log.write(linha + "\n")
            log.write("=" * 60 + "\n")
            pc += 1

        log.write(f"Cycle {pc}\nNo more lines, EOP.\n")

if __name__ == "__main__":
    main()