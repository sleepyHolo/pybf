# -*- coding: utf-8 -*-

from os import system
from time import time
from json import loads
from pybfvm import IOManager, VMCore


class TesterIO(IOManager):
    def __init__(self, test: list) -> None:
        self.max_len = 80
        self.all_test = test
        self.out_msg = []

        self.testing = True
        self.passed = 0
        self.total = 0
        self.next_test()

    def next_test(self) -> None:
        if len(self.all_test) == 0:
            self.testing = False
            return
        self.test = self.all_test.pop()
        self.total += 1

    def input_int(self) -> int:
        return ord(self.test.pop())

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
        print(f' Test {len(self.all_test)} '.center(self.max_len, '=') + '\n')
        print(msg)

    def check(self) -> None:
        if self.out_msg == self.test.pop():
            self.passed += 1
        self.next_test()


class Tester():
    def __init__(self) -> None:
        self.core = VMCore()

    def start_test(self, code: str, test: list) -> float:
        self.code = code
        self.io = TesterIO(test)
        self.core.io = self.io

        self.start = time()
        self.tick = 0
        while self.io.testing:
            self.run()
            self.io.check()
        delta = time() - self.start
        rate = self.io.passed / self.io.total
        print(
            f'Test: {self.io.total}, Pass: {self.io.passed}, Rate: {rate:.4f}')
        print(
            f'Test Time: {delta:.4f}s, {self.tick} ticks, {1000000 * delta / self.tick:.2f} \u03bcs/tick')
        return rate

    def run(self) -> None:
        self.io.out_msg.clear()
        try:
            self.core.run(self.code)
        except SyntaxError as e:
            print(f'SyntaxError: {e}')

        while self.core.is_running():
            self.core.execute()
        self.tick += self.core.time
    
    def test_file(self, name) -> float:
        # code
        code = ''
        with open(name + '.bf', 'r') as fc:
            for c in fc.read():
                if c in '.,><+-[]':
                    code += c
        # test
        with open(name + '.json', 'r') as ft:
            test = loads(ft.read())
        return self.start_test(code, test)


if __name__ == '__main__':
    a = Tester()
    a.test_file('./tmp_files/test')
