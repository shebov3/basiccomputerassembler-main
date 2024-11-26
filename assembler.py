from color import color

class Assembler(object):
    def __init__(self, asmpath='', mripath='', rripath='', ioipath='') -> None:
        super().__init__()
        # Address symbol table dict -> {symbol: location}
        self.__address_symbol_table = {}
        # {LABEL: Location}
        # {
        #  'rot': 10101110101,
        #  'lol': 10101010101
        # }

        # Assembled machine code dict -> {location: binary representation}
        self.__bin = {}
        
        # Load assembly code if the asmpath argument was provided.
        if asmpath:
            self.read_code(asmpath)   
        # memory-reference instructions
        self.__mri_table = self.__load_table(mripath) if mripath else {}
        # register-reference instructions
        self.__rri_table = self.__load_table(rripath) if rripath else {}
        # input-output instructions
        self.__ioi_table = self.__load_table(ioipath) if ioipath else {}
    
    def read_code(self, path:str):
        assert path.endswith('.asm') or path.endswith('.S'), \
                        'file provided does not end with .asm or .S'
        self.__asmfile = path.split('/')[-1] # on unix-like systems
        with open(path, 'r') as f:
            # remove '\n' from each line, convert it to lower case, and split
            # it by the whitespaces between the symbols in that line.
            self.__asm = [s.rstrip().lower().split() for s in f.readlines()]

    def assemble(self, inp='') -> dict:
        assert self.__asm or inp, 'no assembly file provided'
        if inp:
            assert inp.endswith('.asm') or inp.endswith('.S'), \
                        'file provided does not end with .asm or .S'
        # if assembly file was not loaded, load it.
        if not self.__asm:
            self.read_code(inp)
        # remove comments from loaded assembly code.
        self.__rm_comments()
        # do first pass.
        self.__first_pass()
        # do second pass.
        self.__second_pass()
        # The previous two calls should store the assembled binary
        # code inside self.__bin. So the final step is to return
        # self.__bin
        return self.__bin


    # PRIVATE METHODS
    def __load_table(self, path) -> dict:
        with open(path, 'r') as f:
            t = [s.rstrip().lower().split() for s in f.readlines()]
        return {opcode:binary for opcode,binary in t}


    def __islabel(self, string) -> bool:
        return string.endswith(',')


    def __rm_comments(self) -> None:
        for i in range(len(self.__asm)):
            for j in range(len(self.__asm[i])):
                if self.__asm[i][j].startswith('/'):
                    del self.__asm[i][j:]
                    break

    def __format2bin(self, num:str, numformat:str, format_bits:int) -> str:
        if numformat == 'dec':
            return '{:b}'.format(int(num)).zfill(format_bits)
        elif numformat == 'hex':
            return '{:b}'.format(int(num, 16)).zfill(format_bits)
        else:
            raise Exception('format2bin: not supported format provided.')
        

    #! FIRST PASS
    def __first_pass(self) -> None:
        lc = 0 # Location : 0
        for line in (self.__asm):
            if self.__islabel(line[0]):
                self.__address_symbol_table[line[0][:-1]] = self.__format2bin(str(lc),"dec",12)
            elif line[0] == "org":
                lc = int(line[1], 16) # lc = 100
                continue
            elif line[0] == "end":
                break
            lc += 1

        # Debugging
        print(f"\nLOCATION   | LABEL")
        for line in (self.__address_symbol_table):
            print(self.__address_symbol_table[line],line)

        return None

    #! SECOND PASS
    def __second_pass(self) -> None:
        lc = 0
        
        for line in self.__asm:
            if line[0] == "org":
                lc = int(line[1], 16)
                continue
            elif line[0] == "end":
                break
            else:
                instruction = ""
                
                #? Memory reference instruction
                if line[0] in self.__mri_table:
                    address = self.__address_symbol_table[line[1]] # FIRST PASS
                    instruction = "0"+self.__mri_table[line[0]]+address

                #? Register reference instruction
                elif line[0] in self.__rri_table:
                    instruction = self.__rri_table[line[0]]
                elif line[1] in self.__rri_table:
                    instruction = self.__rri_table[line[1]]

                #? Input Output instruction
                elif line[0] in self.__ioi_table:
                    instruction = self.__ioi_table[line[0]]

                #? PSUEDO Instruction
                elif line[1] == "hex":
                    instruction = self.__format2bin(line[2], "hex", 16)
                elif line[1] == "dec":
                    instruction = self.__format2bin(line[2], "dec", 16)

                self.__bin[self.__format2bin(str(lc), "dec", 12)] = instruction

            lc += 1

        # Debugging
        print("\nADDRESS    | INSTRUCTION")
        for key in self.__bin:
            instruction = self.__bin[key]
            print(key, instruction)
        
        return None

INPUT_FILE = 'testcode.asm'
OUT_FILE = 'testcode.mc'
MRI_FILE = 'mri.txt'
RRI_FILE = 'rri.txt'
IOI_FILE = 'ioi.txt'

if __name__ == "__main__":
    bin_text = ''
    asm = Assembler(asmpath=INPUT_FILE,
                    mripath=MRI_FILE,
                    rripath=RRI_FILE,
                    ioipath=IOI_FILE)
    print('Assembling...')
    binaries = asm.assemble()
    for lc in binaries:
        bin_text += lc + '\t' + binaries[lc] + '\n'
    with open(OUT_FILE, 'r') as f:
        print(f'\n{color.GREENBG2}{color.BLACK}{color.ITALIC} TEST PASSED {color.END}' if f.read() == bin_text else f'\n{color.REDBG2}{color.ITALIC}{color.BLACK} TEST FAILED {color.END}')