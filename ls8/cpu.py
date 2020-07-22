"""CPU functionality."""

import sys

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
        }

        self.sp = 7  #index of the stack pointer in register array
        self.reg[self.sp] = -12
        
       

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

    def push(self, op1=None, op2=None):
        self.reg[self.sp] -= 1
        self.ram_write(self.reg[self.sp], self.reg[op1])

    def pop(self, op1=None, op2=None):
        self.reg[op1] = self.ram_read(self.reg[self.sp])
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
        while True:
            self.ir = self.ram_read(self.pc)
            num_bytes = self.ir >> 6
            # >> shift places
            sets_pc = self.ir >> 4 & 0b0001
            is_alu = self.ir >> 5 & 0b001
            self.instruction_set[self.ir](op1=self.ram_read(
                self.pc + 1), op2=self.ram_read(self.pc + 2))
            if not sets_pc:
                self.pc += num_bytes + 1
