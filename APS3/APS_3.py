import copy

# Funções úteis:
def junta_bits(lista_bits):
    return "".join(map(str, lista_bits))

def get_reg(bits):
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
    bits_b_formatado = "".join(map(str, bits))
    return mapeamento_b.get(bits_b_formatado, "nenhum")

# Operadores lógicos da Mic-1
def andLogic(sup, low):
    return 0 if sup == 0 else low

def orLogic(sup, low):
    return 1 if sup == 1 else low

def notLogic(sig):
    return 1 if sig == 0 else 0

def xorLogic(sup, low):
    return 1 if sup != low else 0

def define_Z(saida_ULA):
    for bit in saida_ULA:
        if bit == 1:
            return 0
    return 1

def define_N(f0, f1, co):
    if f0 == 1 and f1 == 1:
        return co
    return 0

def desloca_esquerda_logico(soma):
    saida = [0] * 32
    for i in range(24):
        saida[i] = soma[i + 8]
    return saida

def desloca_direita_aritmetico(soma):
    saida = [0] * 32
    saida[0] = soma[0]
    for i in range(1, 32):
        saida[i] = soma[i - 1]
    return saida

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

def aux_ULA(lista_A, lista_B, sll8, sra1, f0, f1, enA, enB, invA, inc):
    saida_final = [0] * 32
    carry_atual = inc
    for i in range(31, -1, -1):
        bit_A = lista_A[i]
        bit_B = lista_B[i]
        resultado_vai_um, resultado_saida = ULA(bit_A, bit_B, f0, f1, enA, enB, invA, carry_atual)
        saida_final[i] = resultado_saida
        if f0 == 1 and f1 == 1:
            carry_atual = resultado_vai_um
        else:
            carry_atual = 0

    co_final = carry_atual

    if sll8 == 1:
        saida_deslocada = desloca_esquerda_logico(saida_final)
    elif sra1 == 1:
        saida_deslocada = desloca_direita_aritmetico(saida_final)
    else:
        saida_deslocada = saida_final

    z = define_Z(saida_final)
    n = define_N(f0, f1, co_final)
    return saida_final, saida_deslocada, n, z, co_final

def inicializa_entrada(entrada):
    return [int(c) for c in entrada]

def inicializar_registradores(caminho):
    registradores = {
        "mar": [0]*32, "mdr": [0]*32, "pc": [0]*32, "mbr": [0]*8,
        "sp": [0]*32, "lv": [0]*32, "cpp": [0]*32, "tos": [0]*32,
        "opc": [0]*32, "h": [0]*32
    }
    with open(caminho, 'r', encoding='utf-8') as file:
        for linha in file:
            linha = linha.strip()
            if not linha:
                continue
            r, valor = linha.split(' = ')
            registradores[r.lower()] = inicializa_entrada(valor)
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

def mapeamento_barramento_c(regs, barramento_c, sd):
    modificados = []
    # Ordem: H, OPC, TOS, CPP, LV, SP, PC, MDR, MAR
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

def main():
    # Caminhos dos arquivos fornecidos
    arq_dados = "dados_etapa3_tarefa1.txt"
    arq_instrucoes = "microinstruções_etapa3_tarefa1.txt"
    arq_regs = "registradores_etapa3_tarefa1.txt"
    arq_log = "log_etapa3_tarefa1.txt"

    # Carregar memória de dados (16 linhas de 32 bits)
    memoria_dados = carregar_memoria_dados(arq_dados)

    # Carregar instruções (cada linha 23 bits)
    with open(arq_instrucoes, 'r', encoding='utf-8') as f:
        instrucoes = [linha.strip() for linha in f if linha.strip()]

    # Carregar registradores iniciais
    registradores = inicializar_registradores(arq_regs)

    with open(arq_log, 'w', encoding='utf-8') as log:
        # Cabeçalho: estado inicial da memória
        log.write("=" * 60 + "\n")
        log.write("Initial memory state\n")
        log.write("*" * 30 + "\n")
        for linha in memoria_dados:
            log.write(linha + "\n")
        log.write("*" * 30 + "\n")

        # Estado inicial dos registradores
        log.write("Initial register state\n")
        log.write("*" * 30 + "\n")
        ordem_regs = ["mar", "mdr", "pc", "mbr", "sp", "lv", "cpp", "tos", "opc", "h"]
        for nome in ordem_regs:
            log.write(f"{nome} = {junta_bits(registradores[nome])}\n")
        log.write("=" * 60 + "\n")
        log.write("Start of Program\n")
        log.write("=" * 60 + "\n")

        pc = 1
        for instrucao_str in instrucoes:
            # Converter string em lista de bits (23 bits)
            ir = [int(c) for c in instrucao_str]

            # Fatiar a microinstrução
            bits_ula = ir[0:8]         # 8 bits
            bits_c   = ir[8:17]        # 9 bits
            bits_mem = ir[17:19]       # 2 bits: WRITE (X1) / READ (X0)
            bits_b   = ir[19:23]       # 4 bits

            # Controle da ULA
            sll8 = bits_ula[0]
            sra1 = bits_ula[1]
            f0   = bits_ula[2]
            f1   = bits_ula[3]
            enA  = bits_ula[4]
            enB  = bits_ula[5]
            invA = bits_ula[6]
            inc  = bits_ula[7]

            # Verificar combinação inválida SLL8 e SRA1 simultâneos
            if sll8 == 1 and sra1 == 1:
                log.write(f"Cycle {pc}\n")
                log.write(f"ir = {junta_bits(bits_ula)} {junta_bits(bits_c)} {junta_bits(bits_mem)} {junta_bits(bits_b)}\n")
                log.write("> Error, invalid control signals.\n")
                pc += 1
                continue

            # Barramento B
            b = ativa_registrador_b(registradores, bits_b)
            a = registradores["h"]

            # Aplicar habilitações da ULA
            a_eff = a if enA == 1 else [0] * 32
            b_eff = b if enB == 1 else [0] * 32

            # Salvar estado antes da instrução
            regs_antes = copy.deepcopy(registradores)

            # Executar ULA (a saída deslocada é sd)
            _, sd, n, z, co = aux_ULA(a_eff, b_eff, sll8, sra1, f0, f1, enA, enB, invA, inc)

            # Escrever nos registradores via barramento C
            regs_modificados = mapeamento_barramento_c(registradores, bits_c, sd)

            # Operação de memória (após escrita nos registradores)
            if bits_mem[0] == 1:          # WRITE
                endereco = int(junta_bits(registradores["mar"]), 2)
                if 0 <= endereco < len(memoria_dados):
                    memoria_dados[endereco] = junta_bits(registradores["mdr"])
            elif bits_mem[1] == 1:        # READ
                endereco = int(junta_bits(registradores["mar"]), 2)
                if 0 <= endereco < len(memoria_dados):
                    registradores["mdr"] = inicializa_entrada(memoria_dados[endereco])

            # Log do programa
            log.write(f"Cycle {pc}\n")
            log.write(f"ir = {junta_bits(bits_ula)} {junta_bits(bits_c)} {junta_bits(bits_mem)} {junta_bits(bits_b)}\n")
            # Registrador do barramento B
            reg_b_nome = get_reg(bits_b)
            log.write(f"b = {reg_b_nome}\n")
            # Registradores escritos via barramento C
            c_nomes = [nome.lower() for nome in regs_modificados]
            log.write(f"c = {' '.join(c_nomes)}\n")

            log.write("\n> Registers before instruction\n")
            log.write("*" * 30 + "\n")
            for nome in ordem_regs:
                log.write(f"{nome} = {junta_bits(regs_antes[nome])}\n")

            log.write("\n> Registers after instruction\n")
            log.write("*" * 30 + "\n")
            for nome in ordem_regs:
                log.write(f"{nome} = {junta_bits(registradores[nome])}\n")

            log.write("\n> Memory after instruction\n")
            log.write("*" * 30 + "\n")
            for linha in memoria_dados:
                log.write(linha + "\n")
            log.write("=" * 60 + "\n")

            pc += 1

        # Exibe se não tiver nada a ser lido
        log.write(f"Cycle {pc}\n")
        log.write("No more lines, EOP.\n")

main()
