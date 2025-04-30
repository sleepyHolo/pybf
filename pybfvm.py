# -*- coding: utf-8 -*-

"""
25/4/28
Simple Python Brainfxxk VM
25/4/29 test speed: 1.88M operators/s

@author: hxw
"""


class IOManager():
    def __init__(self) -> None:
        self.max_len = 32
    
    def wait_break(self) -> bool:
        return input('Breakpoint. Enter to continue. Input otherwise to stop: ') == ''

    def input_int(self) -> int:
        return ord((input('=> ') + '\n')[0])

    def output_str(self, msg: str) -> None:
        print(msg)

    def output_debug(self, msg: str) -> None:
        print(msg)


class VMCore():
    def __init__(self, io: IOManager = None) -> None:
        self.tape: Tape = Tape()
        self.__running = False
        self.io = IOManager() if io == None else io

    def __pre_check(self) -> None:
        tmp: list = []
        self.jmp_map: dict = {}
        for i, c in enumerate(list(self.__code)):
            if not c in '.,><+-[]':
                raise SyntaxError(f'pos {i}: invalid BrainFxxk code: {c}.')
            if c == '[':
                tmp.append(i)
            elif c == ']':
                if len(tmp) == 0:
                    raise SyntaxError(f"pos {i}: unmatched ']'.")
                self.jmp_map[tmp.pop()] = i
        if not len(tmp) == 0:
            raise SyntaxError(f"pos {tmp.pop()}: '[' was never closed.")
        del tmp

        self.back_map: dict = {}
        for k in self.jmp_map:
            self.back_map[self.jmp_map[k]] = k

    def __run_init(self) -> None:
        self.__pre_check()
        self.tape.clear()
        self.time = 0
        self.ptr = 0
        self.__running = True
        self.output = []

    def execute(self) -> None:
        if not self.__running:
            return
        # breakpoint
        if self.ptr in self.breakpoints:
            self.io.output_debug(self.__debug_log())
            if not self.io.wait_break():
                self.__running = False
                return
        c: str = self.__code[self.ptr]
        if c == '.':
            int_code = self.tape.get_code()
            if int_code == 10:
                self.__output()
            else:
                self.output.append(int_code)
        elif c == ',':
            self.tape.set_code(self.io.input_int())
        elif c == '>':
            self.tape.move_right()
        elif c == '<':
            self.tape.move_left()
        elif c == '+':
            self.tape.add()
        elif c == '-':
            self.tape.sub()
        # jmp
        if c == '[' and self.tape.is_zero():
            self.ptr = self.jmp_map[self.ptr] + 1
        elif c == ']':
            self.ptr = self.back_map[self.ptr]
        else:
            self.ptr += 1
        self.time += 1
        self.__running = self.ptr < len(self.__code)

    def run(self, code: str, breakpoints: list = []) -> None:
        self.__code = code
        self.breakpoints = breakpoints
        self.__run_init()

    def is_running(self) -> bool:
        return self.__running

    def debug_msg(self) -> None:
        self.io.output_debug(self.__debug_log())

    def __debug_log(self) -> str:
        tmp = []
        tmp.append(f'Time: {self.time} '.ljust(self.io.max_len, '='))
        tmp += self.__log_build_code(self.io.max_len)
        tmp += self.tape.info(self.io.max_len)
        tmp.append('> Out : ' + str(self.output))
        return '\n'.join(tmp) + '\n'

    def __log_build_code(self, max_len) -> list:
        if not self.__running:
            return ['> Run : End'.ljust(max_len), ' ' * max_len]
        pre = f'> Run : ({self.ptr}) '
        return [(pre + self.__code[self.ptr: min(len(self.__code),
                                                 self.ptr + max_len - len(pre))]).ljust(max_len),
                (' ' * len(pre) + '^').ljust(max_len)]

    def __output(self):
        self.io.output_str(''.join([chr(int(u)) for u in self.output]))
        self.output.clear()


class uint():
    def __init__(self, num: int, max_: int = 256) -> None:
        self.max_ = max_
        self.num: int = num % self.max_

    def __add__(self, num: int):
        return uint(self.num + num, self.max_)

    def __sub__(self, num: int):
        return uint(self.num - num, self.max_)

    def __str__(self) -> str:
        return str(self.num)

    def __int__(self) -> int:
        return self.num

    def __eq__(self, num: int) -> bool:
        return self.num == num

    def __repr__(self) -> str:
        return ascii(chr(self.num))


class Tape():
    def __init__(self, bit: int = 8) -> None:
        self.__max: int = 2 ** bit
        self.clear()

    def clear(self) -> None:
        self.__ptr: int = 0
        self.__left: list = []
        self.__right: list = []
        # init data
        self.__right.append(uint(0, self.__max))

    def output(self) -> tuple:
        return (len(self.__left) + self.__ptr, self.__left + self.__right)

    def info(self, max_len=32) -> list:
        max_len = max(max_len, 28)
        tab_len = (max_len - 8) // 4
        ascii_len = max_len - 2 * tab_len - 10
        ret = ['| ' + ' Tape Info '.center(max_len - 4, '=') + ' |']
        tab = '|'.join([(' index ' if tab_len > 12 else ' id ').center(tab_len, '+'), '+++',
                        (' int code ' if tab_len >
                         12 else ' int ').center(tab_len, '+'),
                        (' ascii code ' if tab_len > 12 else ' ascii ').center(ascii_len, '+')])
        ret.append(f'| {tab} |')
        self.__left.reverse()
        for i, c in enumerate(self.__left):
            tab = '|'.join([str(i - len(self.__left)).center(tab_len),
                            ' > ' if self.__ptr == i -
                            len(self.__left) else '   ',
                            str(c).center(tab_len), repr(c).center(ascii_len)])
            ret.append(f'| {tab} |')
        self.__left.reverse()
        for i, c in enumerate(self.__right):
            tab = '|'.join([str(i).center(tab_len),
                            ' > ' if self.__ptr == i else '   ',
                            str(c).center(tab_len), repr(c).center(ascii_len)])
            ret.append(f'| {tab} |')
        ret.append('| ' + (max_len - 4) * '=' + ' |')
        return ret

    def __len__(self) -> int:
        return len(self.__left) + len(self.__right)

    def get_code(self) -> uint:
        return self.__left[-self.__ptr - 1] if self.__ptr < 0 else self.__right[self.__ptr]

    def set_code(self, num: int) -> None:
        self.__set(uint(num, self.__max))

    def __set(self, num: uint) -> None:
        if self.__ptr < 0:
            self.__left[-self.__ptr - 1] = num
        else:
            self.__right[self.__ptr] = num

    def is_zero(self) -> bool:
        return self.get_code() == 0

    def move_right(self) -> None:
        self.__ptr += 1
        if self.__ptr >= len(self.__right):
            self.__right.append(uint(0, self.__max))

    def move_left(self) -> None:
        self.__ptr -= 1
        if -self.__ptr > len(self.__left):
            self.__left.append(uint(0, self.__max))

    def add(self) -> None:
        self.__set(self.get_code() + 1)

    def sub(self) -> None:
        self.__set(self.get_code() - 1)


if __name__ == '__main__':
    # hello world
    bfcode = '++++++++++[>+++++++>++++++++++>+++>+<<<<-]>++.>+.+++++++..+++.>++.<<+++++++++++++++.>.+++.------.--------.>+.>.'

    core = VMCore()
    core.run(bfcode)
    while core.is_running():
        core.execute()
