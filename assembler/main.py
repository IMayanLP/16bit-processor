import sys


# adiciona flag no dicionario de flags
def addFlag(flags_list, key, new_flag):
    flags_list[key] = new_flag


# pega uma flag do dicionario e retorna como 8 bits
def getFlag(flag_list, key):
    n = flag_list.get(key)
    return format(n, '08b')

# pega o numero do registrador e retorna como 3 bits
def getRegisNumber(r):
    if r[2] == '0':
        return '000'
    return format(int(r[2]), '03b')

# pega o numero do registrador e retorna como 8 bits
def getRegisNumber_8(r):
    if r[2] == '0':
        return '00000000'
    return format(int(r[2]), '08b')


if __name__ == "__main__":

    flags = {}
    file_name = str(sys.argv[1])
    file = open(file_name, 'r')
    file_name = file_name.split('.')
    hex_file = open((file_name[0]) + '.hex', 'w')
    hex_file.write('v2.0 raw\n')
    Lines = file.readlines()
    l = 0
    last_reg = '000'
    binary_instructions = []
    for line in Lines:
        if '//' in line:
            instructon = line.split('//')
            instruction = instructon[0].split(' ')  # divide a string
        else:
            instruction = line.split(' ')  # divide a string
        # remover espaços e virgulas duplicadas
        i = 0
        while i < len(instruction):
            instruction[i] = instruction[i].replace(',', '')
            if instruction[i] == '':
                instruction.pop(i)
                i = i - 1
            else:
                i = i + 1
        # identifica uma flag
        for i in instruction:
            # identifica uma flag com _ e se o tamanho da instrução for 1 (ftype) adiciona nas flags
            # tambem indentifica se uma linha está vazia para não atrapalhar na contagem de linhas das flags
            if len(instruction) == 1:
                if '_' in i:
                    # adicona no array de flags
                    i = i.replace('\n', '')
                    addFlag(flags, i, l)
                    i += '\n'
                    addFlag(flags, i, l)
                l -= 1
        l += 1

    print(flags)
    for line in Lines:
        # divide os comentarios das linhas de codigo
        if '//' in line:
            instructon = line.split('//')
            instruction = instructon[0].split(' ')  # divide a string
        else:
            instruction = line.split(' ')  # divide a string
        binary = ''  # cria uma string vazia onde vão ser inseridos o opcode, numero dos registradores e imediato
        i = 0
        # remover espaços e virgulas duplicadas
        while i < len(instruction):
            instruction[i] = instruction[i].replace(',', '')
            instruction[i] = instruction[i].replace('\t', '')
            if instruction[i] == '':
                instruction.pop(i)
                i = i - 1
            else:
                i = i + 1
        print(instruction)
        match len(instruction):
            # Divide as instruções pelo tamanho delas
            case 2:
                # unicas instruções com tamanho 2 são o JUMP, RESET e PRINT
                # o JUMP coloca o OP code do jump + 3 digitos inuteis + o endereço imediato em binario
                # o RESET faz um LW com o registrador e o imediato 255
                # o PRINT mostra o registrador passado no display feito no processador
                match instruction[0]:
                    case 'J':
                        binary = '00111' + '000' + getFlag(flags, instruction[1])
                    case 'RESET':
                        binary = '00101' + getRegisNumber(instruction[1]) + format(255, '08b')
                    case 'PRINT':
                        binary = '00011' + getRegisNumber(instruction[1]) + format(0, '08b')

            case 3:
                # divide as instruções de tamanho 3 em dois tipos
                # as que contem flag, que vão ser instrucões branch
                if '_' in instruction[2]:
                    binary = '01000' + getRegisNumber(instruction[1]) + getFlag(flags, instruction[2])
                else:
                    # se não contem flag checamos a terceira posição para saber se é um LW ou SW com um registrador
                    if '$r' in instruction[2]:
                        match instruction[0]:
                            case 'LW':
                                binary += '10101'
                            case 'SW':
                                binary += '10110'
                        binary += getRegisNumber(instruction[1]) + getRegisNumber_8(instruction[2])
                    else:
                        # se não for, por fim comparamos a instrução com as possiveis instruções de tamanho 3
                        match instruction[0]:
                            case 'ADDI':
                                binary += '00011'
                            case 'SUBI':
                                binary += '00100'
                            case 'LW':
                                binary += '00101'
                            case 'SW':
                                # caso tente carregar o valor 255 num registrador ele sai do programa
                                # visto que esse valor é reservado para o RESET
                                if int(instruction[2]) >= 255:
                                    print('Erro na linha ' + str(Lines.index(line) + 1) + ': não é possivel carregar '
                                                                                          'valores '
                                                                                          'maiores que 254')
                                    sys.exit()

                                binary += '00110'

                        binary += getRegisNumber(instruction[1]) + format(int(instruction[2]), '08b')

            case 4:
                # caso o tamanho da instrução seja 4 temos essas 3 possiblidades que são do tipo R
                match instruction[0]:
                    case 'SLT':
                        binary += '00010'
                    case 'ADD':
                        binary += '00000'
                    case 'SUB':
                        binary += '00001'
                # então depois de adicionar o opcode na string adicionamos o valor dos 3 registradores
                # e dois bits que não são usados no final
                binary += getRegisNumber(instruction[1]) + getRegisNumber(instruction[2])
                binary += getRegisNumber(instruction[3]) + '00'
            # toda vez que realizamos uma instrução que não é um Jump salvamos o numero do ultimo registrador
            # em uma variavel
        if instruction[0] != 'J' and len(instruction) > 1:
            last_reg = getRegisNumber(instruction[1])
        # Se a string binaria não estiver vazia, o que acontece quando a linha não existe, adicionamos ela na lista
        if binary != '':
            binary_instructions.append(binary)
    # e por ultimo adicionamos uma instrução que para o clock passando o ultimo registrador utilizado
    # para que ele apareça no display do processador
    binary_instructions.append('11111' + last_reg + '00000000')
    # processo de conversão de binario para hexa-decimal
    for b in binary_instructions:
        hex_file.write(hex(int(b, 2))[2:].zfill(4))
        hex_file.write('\n')

    hex_file.close()
    # salvando o arquivo .hex
