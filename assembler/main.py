import sys


def addFlag(flags_list, key, new_flag):
    flags_list[key] = new_flag


def getFlag(flag_list, key):
    n = flag_list.get(key)
    return format(n, '08b')


def getRegisNumber(r):
    if r[2] == '0':
        return '000'
    return format(int(r[2]), '03b')

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
            if '_' in i and len(instruction) == 1:
                # adicona no array de flags
                i = i.replace('\n', '')
                addFlag(flags, i, l)
                i += '\n'
                addFlag(flags, i, l)
                l -= 1
        l += 1
    print(flags)
    for line in Lines:
        if '//' in line:
            instructon = line.split('//')
            instruction = instructon[0].split(' ')  # divide a string
        else:
            instruction = line.split(' ')  # divide a string
        binary = ''
        # remover espaços e virgulas duplicadas
        i = 0
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
                match instruction[0]:
                    case 'J':
                        binary = '00111' + '000' + getFlag(flags, instruction[1])
                    case 'RESET':
                        binary = '00101' + getRegisNumber(instruction[1]) + format(255, '08b')
                    case 'PRINT':
                        binary = '00011' + getRegisNumber(instruction[1]) + format(0, '08b')

            case 3:
                # divide as instruções de tamanho 3 em dois tipos
                if '_' in instruction[2]:
                    binary = '01000' + getRegisNumber(instruction[1]) + getFlag(flags, instruction[2])
                else:
                    if '$r' in instruction[2]:
                        match instruction[0]:
                            case 'LW':
                                binary += '10101'
                            case 'SW':
                                binary += '10110'
                        binary += getRegisNumber(instruction[1]) + getRegisNumber_8(instruction[2])
                    else:
                        match instruction[0]:
                            case 'ADDI':
                                binary += '00011'
                            case 'SUBI':
                                binary += '00100'
                            case 'LW':
                                binary += '00101'
                            case 'SW':
                                if int(instruction[2]) >= 255:
                                    print('Erro na linha ' + str(Lines.index(line) + 1) + ': não é possivel carregar '
                                                                                          'valores '
                                                                                          'maiores que 254')
                                    sys.exit()

                                binary += '00110'

                        binary += getRegisNumber(instruction[1]) + format(int(instruction[2]), '08b')

            case 4:
                match instruction[0]:
                    case 'SLT':
                        binary += '00010'
                    case 'ADD':
                        binary += '00000'
                    case 'SUB':
                        binary += '00001'
                binary += getRegisNumber(instruction[1]) + getRegisNumber(instruction[2])
                binary += getRegisNumber(instruction[3]) + '00'
        if instruction[0] != 'J' and len(instruction) > 1:
            last_reg = getRegisNumber(instruction[1])
        if binary != '':
            binary_instructions.append(binary)
    binary_instructions.append('11111' + last_reg + '00000000')
    for b in binary_instructions:
        hex_file.write(hex(int(b, 2))[2:].zfill(4))
        hex_file.write('\n')

    hex_file.close()
