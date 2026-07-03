import copy
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from APS3.APS_3 import *

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
                
                byte_val = int(byte_arg)
                byte_bin = bin(byte_val & 0xff)[2:].zfill(8)
                instrucao_especial = byte_bin + "000000000110000"
                microinstrucoes_finais.append(instrucao_especial)
                
                microinstrucoes_finais.append("00111000001000010100000")     # MDR = TOS = H; wr

    return microinstrucoes_finais

def main():
    diretorio_script = os.path.dirname(os.path.abspath(__file__))
    diretorio_pai = os.path.dirname(diretorio_script)

    arq_dados = os.path.join(diretorio_pai, "APS3", "dados_etapa3_tarefa1.txt")
    arq_regs = os.path.join(diretorio_pai, "APS3", "registradores_etapa3_tarefa1.txt")
    arq_instrucoes = os.path.join(diretorio_script, "instruções.txt")
    arq_log = os.path.join(diretorio_script, "log_Entrega_Final.txt")

    memoria_dados = carregar_memoria_dados(arq_dados)
    registradores = inicializar_registradores(arq_regs)
    
    # aplica a função para traduzir os 23 bits para instruções de 32 bits
    instrucoes_23_bits = traduzir_instrucoes(arq_instrucoes)

    with open(arq_log, 'w', encoding='utf-8') as log:
        log.write("=" * 60 + "\nInitial memory state\n" + "*" * 30 + "\n")
        for linha in memoria_dados: log.write(linha + "\n")
        log.write("*" * 30 + "\nInitial register state\n" + "*" * 30 + "\n")
        
        ordem_regs = ["mar", "mdr", "pc", "mbr", "sp", "lv", "cpp", "tos", "opc", "h"]
        for nome in ordem_regs: log.write(f"{nome} = {junta_bits(registradores[nome])}\n")
        
        log.write("=" * 60 + "\nStart of Program\n" + "=" * 60 + "\n")

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
                pc += 1
                continue

            sll8, sra1, f0, f1, enA, enB, invA, inc = bits_ula

            if sll8 == 1 and sra1 == 1:
                log.write(f"Cycle {pc}\nir = {junta_bits(bits_ula)} {junta_bits(bits_c)} {junta_bits(bits_mem)} {junta_bits(bits_b)}\n> Error, invalid control signals.\n")
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
            
            log.write("\n> Registers before instruction\n" + "*" * 30 + "\n")
            for nome in ordem_regs: log.write(f"{nome} = {junta_bits(regs_antes[nome])}\n")

            log.write("\n> Registers after instruction\n" + "*" * 30 + "\n")
            for nome in ordem_regs: log.write(f"{nome} = {junta_bits(registradores[nome])}\n")

            log.write("\n> Memory after instruction\n" + "*" * 30 + "\n")
            for linha in memoria_dados: log.write(linha + "\n")
            log.write("=" * 60 + "\n")
            pc += 1

        log.write(f"Cycle {pc}\nNo more lines, EOP.\n")

if __name__ == "__main__":
    main()