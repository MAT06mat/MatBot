import string, random


printable = list(char for char in string.printable if char not in ("\t", "\r", "\x0b", "\x0c", "\n"))
printable.extend(("ù", "¤", "£", "§", "è", "é", "ê", "â", "à", "ç", "ï", "î", "²", "°", "µ"))


class CriptTable:
    def __init__(self, seed) -> None:
        self.set_seed(seed)
    
    def set_seed(self, seed: int | float | str | bytes | bytearray | None) -> None:
        self.seed = seed
        random.seed(seed)
        
        all_chars: list = random.sample(printable, len(printable))
        self.list_1: list = random.sample(all_chars, int(len(all_chars)/2))
        self.list_2: list = [char for char in all_chars if char not in self.list_1]

    def translate(self, text: str) -> str:
        new_text = ""
        
        for char in text:
            new_char = ""
            if char in self.list_1:
                new_char: str = self.list_2[self.list_1.index(char)]
            elif char in self.list_2:
                new_char: str = self.list_1[self.list_2.index(char)]
            else:
                new_char: str = char
            
            new_text += new_char
        
        return new_text