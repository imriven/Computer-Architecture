"""CPU functionality."""

import sys
import datetime

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.reg = [0] * 8
        self.ram = [0] * 256
        self.pc = 0
        self.ir = 0
        self.instruction_set = {
            0b10000010: self.ldi,
            0b01000111: self.prn,
            0b1: self.hlt,
            0b10100010: self.mul,
            0b01000101: self.push,
            0b01000110: self.pop,
            0b01010000: self.call,
            0b00010001: self.ret,
            0b10100000: self.add,
            0b10000100: self.st,
            0b01010100: self.jmp,
            0b01001000: self.pra,
            0b00010011: self.iret,
        }

        self.sp = 7  #index of the stack pointer in register array
        self.istatus = 6
        self.im = 5
        self.reg[self.sp] = -12
        self.fl = 0
        
        self.interrupts_enabled = True
       

    def load(self, file_to_open):
        """Load a program into memory."""

        address = 0

        # For now, we've just hardcoded a program:

        # program = [
        #     # From print8.ls8
        #     0b10000010, # LDI R0,8
        #     0b00000000,
        #     0b00001000,
        #     0b01000111, # PRN R0
        #     0b00000000,
        #     0b00000001, # HLT
        # ]

        with open(file_to_open, "r") as f:
            program = f.readlines()


        for instruction in program:
            if instruction.startswith("#"):
                continue
            self.ram[address] = int(instruction.split(" ")[0], 2)
            address += 1
        
    def mul(self, op1=None, op2=None):
        self.alu("MUL", op1, op2)

    def add(self, op1=None, op2=None):
        self.alu("ADD", op1, op2)

    def push(self, op1=None, op2=None):
        self.reg[self.sp] -= 1
        self.ram_write(self.reg[self.sp], self.reg[op1])

    def pop(self, op1=None, op2=None):
        self.reg[op1] = self.ram_read(self.reg[self.sp])
        self.reg[self.sp] += 1

    def call(self, op1=None, op2=None):
        self.reg[self.sp] -= 1
        self.ram_write(self.reg[self.sp], self.pc + 2)
        self.pc = self.reg[op1]

    def ret(self, op1=None, op2=None):
        self.pc = self.ram_read(self.reg[self.sp])
        self.reg[self.sp] += 1

    def ram_read(self, mar):
        return self.ram[mar]

    def ram_write(self, mar, mdr):
        self.ram[mar] = mdr

    def ldi(self, op1=None, op2=None):
        self.reg[op1] = op2

    def prn(self, op1=None, op2=None):
        print(self.reg[op1])

    def hlt(self, op1=None, op2=None):
        sys.exit()

    def st(self, op1=None, op2=None):
        self.ram_write(self.reg[op1], self.reg[op2])

    def jmp(self, op1=None, op2=None):
        self.pc = self.reg[op1]

    def pra(self, op1=None, op2=None):
        print(chr(self.reg[op1]))

    def iret(self, op1=None, op2=None):
        for r in range(6, -1, -1):
            self.reg[r] = self.ram_read(self.reg[self.sp])
            self.reg[self.sp] += 1
        self.reg[self.fl] = self.ram_read(self.reg[self.sp])
        self.reg[self.sp] += 1
        self.pc = self.ram_read(self.reg[self.sp])
        self.reg[self.sp] += 1
        self.interrupts_enabled = True

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        #elif op == "SUB": etc
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        now = datetime.datetime.now()
        while True:
            if datetime.datetime.now() > now + datetime.timedelta(0, 1):
                self.reg[self.istatus] = self.reg[self.istatus] | 0b1
                now = datetime.datetime.now()
            
            if self.interrupts_enabled:
                masked_interrupts = self.reg[self.im] & self.reg[self.istatus]
                for i in range(8):
                    # Right shift interrupts down by i, then mask with 1 to see if that bit was set
                    interrupt_happened = ((masked_interrupts >> i) & 1) == 1
                    if not interrupt_happened:
                        continue 
                    self.interrupts_enabled = False
                    self.reg[self.istatus] = self.reg[self.istatus] & 2^i
                    self.reg[self.sp] -= 1
                    self.ram_write(self.reg[self.sp], self.pc)
                    self.reg[self.sp] -= 1
                    self.ram_write(self.reg[self.sp], self.fl)
                    for r in range(7):
                        self.reg[self.sp] -= 1
                        self.ram_write(self.reg[self.sp], self.reg[r])
                    self.pc = self.ram_read(-(8 - i))
                    break

            self.ir = self.ram_read(self.pc)
            num_bytes = self.ir >> 6
            # >> shift places
            sets_pc = self.ir >> 4 & 0b0001
            is_alu = self.ir >> 5 & 0b001
            self.instruction_set[self.ir](op1=self.ram_read(
                self.pc + 1), op2=self.ram_read(self.pc + 2))
            if not sets_pc:
                self.pc += num_bytes + 1
