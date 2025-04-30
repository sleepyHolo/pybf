# -*- coding: utf-8 -*-

from os import system, path
from time import sleep
from pybfvm import IOManager, VMCore


class ConsoleIO(IOManager):
    def __init__(self) -> None:
        self.max_len = 80
        self.out_msg = []

    def output_str(self, msg: str) -> None:
        self.out_msg.append(msg)

    def log(self) -> None:
        print()
        print(' Output '.center(self.max_len, '='))
        for msg in self.out_msg:
            print('> ' + msg.ljust(self.max_len - 2))
        print()

    def output_debug(self, msg: str) -> None:
        system('cls')
        print(msg)


class BFConsole():
    bfcodes = {
        'hello': '++++++++++[>+++++++>++++++++++>+++>+<<<<-]>++.>+.+++++++..+++.>++.<<+++++++++++++++.>.+++.------.--------.>+.>.'
    }
    bfmsg = {'hello': 'print Hello World!'}

    def __init__(self) -> None:
        self.io = ConsoleIO()
        self.core = VMCore(self.io)
        self.sleep_time = 0.01
        self.files = {}
        self.file_msgs = {}

        system('cls')
        self.__wait_order()

    def run(self, code: str, breakpoints: list) -> None:
        self.io.out_msg.clear()
        try:
            self.core.run(code, breakpoints=breakpoints)
        except SyntaxError as e:
            print(f'SyntaxError: {e}')

        self.core.debug_msg()
        self.io.log()
        while self.core.is_running():
            self.core.execute()
            sleep(self.sleep_time)
            self.core.debug_msg()
            self.io.log()
        self.__wait_order()

    def __wait_order(self) -> None:
        print('\n' + ' Console '.center(self.io.max_len, '='))
        while not self.__parse(input('Input: ').split(' ')):
            print('\n' + ' Console '.center(self.io.max_len, '='))

    def __parse(self, input_: list) -> bool:
        if input_[0] == 'quit':
            return True
        try:
            if input_[0] == 'run':
                self.__parse_run(input_[1:])
                return True
            if input_[0] == 'open':
                self.__open(input_[1], ' '.join(input_[2:]))
                return True
            if input_[0] == 'help':
                system('cls')
                self.__config_msg()
                self.__help_msg()
                return False
            if input_[0] == 'set':
                self.__perse_set(input_[1:])
                return False
            if input_[0] == 'list':
                self.__file_msg()
                return False
            print('Unable to parse. Type help for more info.')
            return False
        except Exception as e:
            print(e)
            return False

    def __parse_run(self, input_: list) -> None:
        bks = [int(x) for x in input_[1:]]
        if input_[0] in self.files:
            self.run(self.files[input_[0]], bks)
            return
        if input_[0] in BFConsole.bfcodes:
            self.run(BFConsole.bfcodes[input_[0]], bks)
            return
        self.run(input_[0], bks)

    def __perse_set(self, input_: list) -> None:
        if input_[0] == 'width':
            self.io.max_len = max(40, int(input_[1]))
            print(f'new width: {self.io.max_len} chars')
        if input_[0] == 'sleep':
            self.sleep_time = max(0, float(input_[1]))
            print(f'new sleep time: {self.sleep_time} s')

    def __help_msg(self) -> None:
        print('\n'.join([' Console Help '.center(self.io.max_len, '-'),
                         '> quit',
                         '  quit. you can also use ctrl+c to stop executing.',
                         '> run file/code [breakpoints..]',
                         '  run brainfxxk code or run code file.',
                         '> set option setting',
                         '  option:',
                         '  > width: change max display width (min 40 chars).',
                         '  > sleep: change sleep time (s) after operation.',
                         '> open filename [massage]',
                         '  load a file. then you can run with name.',
                         '> list',
                         '  show valid files.']))

    def __file_msg(self) -> None:
        system('cls')
        print(' Files Info '.center(self.io.max_len, '='))
        tab_len = (self.io.max_len - 6) // 4
        msg_len = self.io.max_len - 2 * tab_len - 6
        print('| ' + '|'.join([' file '.center(tab_len, '+'),
                               ' info '.center(tab_len, '+'),
                               ' massage '.center(msg_len, '+')]) + ' |')
        tmp = []
        for f in self.files:
            tmp.append('| ' + '|'.join([f.center(tab_len),
                                        'loaded'.center(tab_len),
                                        self.file_msgs[f].center(msg_len)]) + ' |')
        for f in BFConsole.bfcodes:
            if f in self.files:
                continue
            tmp.append('| ' + '|'.join([f.center(tab_len),
                                        'built-in'.center(tab_len),
                                        BFConsole.bfmsg[f].center(msg_len)]) + ' |')
        tmp.sort(key=lambda x: x.split('|')[1].lstrip())
        tmp.append('| ' + '=' * (self.io.max_len - 4) + ' |')
        print('\n'.join(tmp))

    def __config_msg(self) -> None:
        print('\n'.join([' Console Info '.center(self.io.max_len, '-'),
                         f'> speed: {1/(self.sleep_time+0.013):.1f} operators/s',
                         f'    (sleep {self.sleep_time:.4f}s after every step)',
                         f'> width: {self.io.max_len} chars']))

    def __open(self, file: str, msg: str = '') -> None:
        code = ''
        with open(file) as f:
            for c in f.read():
                if c in '.,><+-[]':
                    code += c
        self.files[path.splitext(file)[0]] = code
        self.file_msgs[path.splitext(file)[0]] = msg
        self.__wait_order()


if __name__ == '__main__':
    BFConsole()
