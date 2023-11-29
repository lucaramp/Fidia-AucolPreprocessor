from typing import List, Tuple
from ListQueue import ListQueue
import os


class Preporcessor:
    __IFDEF_DIR = '.IFDF'
    __ENDIF_DIR = '.ENDC'
    __INCLUDE_DIR = ".INCLUDE"
    EMPTY_LINE_TAG = 'Empty Line'
    __DEFINE_DIR = "#define"
    def __init__(self):
        #nomi dei file vuoti da utilizzare
        self.file_name = ''
        self.dirName = ''
        self.file_name_no_comm = ''
        self.file_name_include = ''
        self.file_name_tokens = ''
        self.file_name_defines = ''
        self.file_name_out = ''

        self.input_orig = list()
        self.input_noComm = list()
        self.input_with_include = list()
        self.output_processed = list()
        self.output_processed_whit_blank = list()
        self.tokenized = [['']]
        self.define_table = {"name": None}
        pass

    def setOriginalFileName(self,dir : str,name : str)->None:
        self.file_name = name
        self.dirName = dir
        self.file_name_no_comm = os.path.splitext(name)[0] + '_no_comment' + os.path.splitext(name)[1]
        self.file_name_include = os.path.splitext(name)[0] + '_include' + os.path.splitext(name)[1]
        self.file_name_tokens = os.path.splitext(name)[0] + '_tok' + os.path.splitext(name)[1]
        self.file_name_defines = os.path.splitext(name)[0] + '_defines' + os.path.splitext(name)[1]
        self.file_name_out = os.path.splitext(name)[0] + '_out' + os.path.splitext(name)[1]
        self.file_name_out_diff = os.path.splitext(name)[0] + '_out_diff' + os.path.splitext(name)[1]

    def GenerateProcessed(self) -> bool:
        if len(self.input_orig) == 0:
            return False
        ifDef_queue = ListQueue()

        ifDef_queue.put(True)

        for line in self.input_orig:
            bMustInsert = ifDef_queue.peek()
            tokens = line.split()
            bIsAnOpen, bIsDirectiveTrue = self.isOpenDirective(tokens,line)
            # se trova un .IFDF
            if bIsAnOpen:
                # non iserisce la linea con la direttiva ma la mette per il diff
                ifDef_queue.put(bIsDirectiveTrue)
                self.output_processed_whit_blank.append(Preporcessor.EMPTY_LINE_TAG + "\n")
            else:
                bIsAClose = self.isCloseDirective(tokens)
                # se trova .ENDIF
                if bIsAClose:
                    # toglie l'ultima direttiva dalla coda e non aggiunge la linea
                    # ma la mette per il diff
                    self.output_processed_whit_blank.append(Preporcessor.EMPTY_LINE_TAG + "\n")
                    ifDef_queue.get()
                else:
                    # se trova una linea nosrmale la inserisce solo se la coda contiene True
                    if bMustInsert:
                        self.output_processed.append(line)
                        self.output_processed_whit_blank.append(line)
                    else:
                        # skippa ovvero non fa nulla (lo appende solo nel file per i diff)
                        self.output_processed_whit_blank.append(Preporcessor.EMPTY_LINE_TAG + "\n")
                        pass
        # se esco dal for voglio che tutti gli ifdef siano bilanciati dagli endif
        if ifDef_queue.size() != 1:
            print(f"Unbalanced {self.__IFDEF_DIR}/{self.__ENDIF_DIR} Queue size {ifDef_queue.size()}")
            return False

        with open(self.dirName + os.sep + self.file_name_out, 'wt') as w:
            for line in self.output_processed:
                line = str(line) #+ '\n'
                w.write(line)

        print(f"Created {self.file_name_out} ...with {len(self.output_processed)} lines")

        with open(self.dirName + os.sep + self.file_name_out_diff, 'wt') as w:
            for line in self.output_processed_whit_blank:
                line = str(line) #+ '\n'
                w.write(line)

        print(f"Created {self.file_name_out_diff} ...with {len(self.output_processed_whit_blank)} lines")

        return True

    def ParceDirectives(self)->bool:
        print(self.file_name, self.file_name_no_comm)

        with open(self.dirName + os.sep + self.file_name, 'r') as inp:
            self.input_orig = inp.readlines()

        print(f"Read {self.file_name} ... {len(self.input_orig)} lines")

        if not self.unComment(self.input_orig, self.input_noComm):
            print("no comment found")

        with open(self.dirName + os.sep + self.file_name_no_comm, 'wt') as w:
            w.writelines(self.input_noComm)

        print(f"Created {self.file_name_no_comm} ...with {len(self.input_noComm)} lines")

        if not self.withIncludeFiles(self.input_noComm, self.input_with_include, self.dirName, self.tokenized):
            print("no include found")

        with open(self.dirName + os.sep + self.file_name_include, 'wt') as w:
            w.writelines(self.input_with_include)

        print(f"Created {self.file_name_include} ...with {len(self.input_with_include)} lines")

        with open(self.dirName + os.sep + self.file_name_tokens, 'wt') as w:
            for tokens in self.tokenized:
                line = str(tokens) + '\n'
                w.write(line)

        print(f"Created {self.file_name_tokens} ...with {len(self.tokenized)} lines")

        self.parceDefines(self.tokenized, self.define_table)

        with open(self.dirName + os.sep + self.file_name_defines, 'wt') as w:
            for Nome, Val in self.define_table.items():
                strLine = f" {Nome} = {Val}\n"
                w.write(strLine)

        print(f"Created {self.file_name_defines} ...with {len(self.define_table)} lines")
        return True

    def isOpenDirective(self, line_token: list, line:str ) -> Tuple[bool, bool]:
        #se hra meno di 2 token non puo esserlo sicuramente
        if len(line_token) < 2:
            return False,False
        #il primo deve essere per forz .IFDF
        if line_token[0] != self.__IFDEF_DIR:
            return False, False
        line_semicolon = line.split(';')
        #ho la stringa linea senza commenti
        line = line_semicolon[0]
        line_token2=line.split()
        #ripeto il test per scrupolo prima di scartarlo
        if line_token2[0] != self.__IFDEF_DIR or len(line_token) <= 1:
            return False, False
        #ora splittando con = dovrei avere la condizione
        line = ' '.join(line_token2[1:])
        line_token2 = line.split('=')
        name = 'None'
        value = None
        #ho solo ifdef senza =
        if len(line_token2) == 1:
            name = line_token2[0]
            return True, self.isDefined(name,value)
        if len(line_token2) > 1:
            name = line_token2[0].strip()
            value = line_token2[1].strip()
            if not value.isdigit():
                print(f"ERROR: CONVERSION OF {value} to INT pacing {' '.join(line_token)}")
                return False, False
            return True,self.isDefined(name, int(value) )
        #non va mai qui
        return False,False

    def isCloseDirective(self, line_token: list) -> bool:
        if len(line_token)<1:
            return False
        if line_token[0]!=self.__ENDIF_DIR:
            return False
        return True

    def isDefined(self, name: str, value: int = None) -> bool:
        if name in self.define_table.keys():
            if value is not None:
                return self.define_table[name] == value
            else:
                return True
        else:
            return False

    def setDefine(self, name: str, value: int = None, undef: bool = False) -> None:
        if not undef:
            self.define_table[name] = value
        else:
            self.define_table.pop(name, d=None)
        return None

    def unComment(self, source: list, destination: list, onlyComments: list = list()) -> bool:
        for line in source:
            splitted = line.split(sep=';', maxsplit=2)
            strNoCom, strComm = '', ''
            if len(splitted) == 1:
                strNoCom = splitted[0]
                strComm = str()
            else:
                strNoCom, strComm = splitted[0], splitted[1]

            if len(strNoCom) != 0 and not strNoCom.endswith('\n'):
                strNoCom += '\n'
            if len(strComm) != 0 and not strComm.endswith('\n'):
                strNoCom += '\n'
            destination.append(strNoCom)
            onlyComments.append(strComm)

        return len(onlyComments) != 0

    def withIncludeFiles(self, source: list, dest: list, dir: str = "", tokenized: List[List[str]] = [['']]) -> bool:
        self.tokenized.clear()
        for line in source:
            tokens = line.split()
            index = -1
            try:
                index = tokens.index(self.__INCLUDE_DIR)
            except:
                pass
            if index >= 0:
                print(f"Trovato include in {tokens}")
                bFound = True
                try:
                    include_file_name = tokens[index + 1]
                except:
                    bFound = False
                if bFound:
                    include_file_name = include_file_name.strip('"')
                    included, included_noComment = list(), list()
                    with open(dir + os.sep + include_file_name, "r") as inc_file:
                        included = inc_file.readlines()
                    self.unComment(included, included_noComment)
                    for inc_line in included_noComment:
                        inc_token = inc_line.split()
                        if len(inc_token) > 0:
                            tokenized.append(inc_token)
                        dest.append(inc_line)
                else:
                    print("Found .INCLUDE with no FILE. SKIPPED")
            else:
                dest.append(line)
                if len(tokens) > 0:
                    tokenized.append(tokens)
        return True

    def parceDefines(self, tokenized_source: List[List[str]], define_table: dict()) -> bool:
        define_table.clear()
        for tok_row in tokenized_source:
            def_idx = -1
            try:
                def_idx = tok_row.index(self.__DEFINE_DIR)
            except:
                def_idx = -1
            if def_idx >= 0:
                bDefNamePresent = True
                bValPresent = True
                try:
                    Name = str(tok_row[def_idx + 1])
                    try:
                        Val = int(tok_row[def_idx + 2])
                    except:
                        bValPresent = False
                except:
                    bDefNamePresent = False
                if bDefNamePresent and bValPresent:
                    define_table[Name] = Val
                if bDefNamePresent and not bValPresent:
                    define_table[Name] = None
        pass