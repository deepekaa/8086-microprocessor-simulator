
from dataclasses import dataclass, field
import re

MASK16 = 0xFFFF
SIGN16 = 0x8000


@dataclass
class CPU8086:
    registers: dict = field(default_factory=lambda: {
        "AX": 0, "BX": 0, "CX": 0, "DX": 0,
        "SP": 0xFFFE, "BP": 0, "SI": 0, "DI": 0,
    })

    flags: dict = field(default_factory=lambda: {
        "CF": 0, "ZF": 0, "SF": 0, "OF": 0,
    })

    program: list = field(default_factory=list)
    labels: dict = field(default_factory=dict)
    ip: int = 0
    halted: bool = False
    history: list = field(default_factory=list)

    def reset(self):
        self.registers = {
            "AX": 0, "BX": 0, "CX": 0, "DX": 0,
            "SP": 0xFFFE, "BP": 0, "SI": 0, "DI": 0,
        }
        self.flags = {"CF": 0, "ZF": 0, "SF": 0, "OF": 0}
        self.ip = 0
        self.halted = False
        self.history = []

    def load_program(self, source):
        self.program = []
        self.labels = {}
        self.ip = 0
        self.halted = False
        self.history = []

        for raw_line in source.splitlines():
            line = raw_line.split(";", 1)[0].strip()
            if not line:
                continue

            while ":" in line:
                label_part, rest = line.split(":", 1)
                label = label_part.strip().upper()

                if not re.fullmatch(r"[A-Z_][A-Z0-9_]*", label):
                    raise ValueError(f"Invalid label: {label}")

                if label in self.labels:
                    raise ValueError(f"Duplicate label: {label}")

                self.labels[label] = len(self.program)
                line = rest.strip()

                if not line:
                    break

            if line:
                self.program.append(line)

    def parse_value(self, value):
        value = value.strip().upper()

        if value in self.registers:
            return self.registers[value]

        try:
            if value.endswith("H"):
                return int(value[:-1], 16) & MASK16
            if value.startswith("0X"):
                return int(value, 16) & MASK16
            return int(value, 10) & MASK16
        except ValueError:
            raise ValueError(f"Invalid operand: {value}")

    def set_register(self, register, value):
        register = register.upper()
        if register not in self.registers:
            raise ValueError(f"Unknown register: {register}")
        self.registers[register] = value & MASK16

    def update_common_flags(self, result):
        result &= MASK16
        self.flags["ZF"] = int(result == 0)
        self.flags["SF"] = int(bool(result & SIGN16))

    def add16(self, a, b):
        full_result = a + b
        result = full_result & MASK16

        self.flags["CF"] = int(full_result > MASK16)
        self.flags["OF"] = int(
            bool((~(a ^ b) & (a ^ result)) & SIGN16)
        )
        self.update_common_flags(result)
        return result

    def sub16(self, a, b):
        result = (a - b) & MASK16

        self.flags["CF"] = int(a < b)
        self.flags["OF"] = int(
            bool(((a ^ b) & (a ^ result)) & SIGN16)
        )
        self.update_common_flags(result)
        return result

    def logic_flags(self, result):
        self.flags["CF"] = 0
        self.flags["OF"] = 0
        self.update_common_flags(result)

    def parse_instruction(self, instruction):
        parts = instruction.strip().split(None, 1)
        opcode = parts[0].upper()
        operands = []

        if len(parts) > 1:
            operands = [x.strip() for x in parts[1].split(",")]

        return opcode, operands

    def require_operands(self, opcode, operands, count):
        if len(operands) != count:
            raise ValueError(
                f"{opcode} expects {count} operand(s)."
            )

    def jump_to(self, label):
        label = label.strip().upper()
        if label not in self.labels:
            raise ValueError(f"Unknown label: {label}")
        self.ip = self.labels[label]

    def step(self):
        if self.halted:
            return "Program already halted."

        if self.ip >= len(self.program):
            self.halted = True
            return "End of program."

        current_ip = self.ip
        instruction = self.program[current_ip]
        opcode, operands = self.parse_instruction(instruction)

        # Default: advance to the next instruction.
        self.ip += 1

        if opcode == "MOV":
            self.require_operands(opcode, operands, 2)
            self.set_register(
                operands[0], self.parse_value(operands[1])
            )

        elif opcode in ("ADD", "SUB", "AND", "OR", "XOR"):
            self.require_operands(opcode, operands, 2)
            dest = operands[0].upper()

            if dest not in self.registers:
                raise ValueError(
                    f"{opcode} destination must be a register."
                )

            a = self.registers[dest]
            b = self.parse_value(operands[1])

            if opcode == "ADD":
                result = self.add16(a, b)
            elif opcode == "SUB":
                result = self.sub16(a, b)
            elif opcode == "AND":
                result = a & b
                self.logic_flags(result)
            elif opcode == "OR":
                result = a | b
                self.logic_flags(result)
            else:
                result = a ^ b
                self.logic_flags(result)

            self.registers[dest] = result & MASK16

        elif opcode in ("INC", "DEC"):
            self.require_operands(opcode, operands, 1)
            dest = operands[0].upper()

            if dest not in self.registers:
                raise ValueError(
                    f"{opcode} destination must be a register."
                )

            old_cf = self.flags["CF"]
            value = self.registers[dest]

            if opcode == "INC":
                result = self.add16(value, 1)
            else:
                result = self.sub16(value, 1)

            self.registers[dest] = result
            self.flags["CF"] = old_cf

        elif opcode == "CMP":
            self.require_operands(opcode, operands, 2)
            a = self.parse_value(operands[0])
            b = self.parse_value(operands[1])
            self.sub16(a, b)

        elif opcode == "JMP":
            self.require_operands(opcode, operands, 1)
            self.jump_to(operands[0])

        elif opcode in ("JZ", "JE", "JNZ", "JNE", "JC", "JNC"):
            self.require_operands(opcode, operands, 1)
            flag = self.flags["ZF"] if opcode in ("JZ", "JE", "JNZ", "JNE") else self.flags["CF"]

            should_jump = (
                flag == 1 if opcode in ("JZ", "JE", "JC")
                else flag == 0
            )

            if should_jump:
                self.jump_to(operands[0])

        elif opcode == "NOP":
            self.require_operands(opcode, operands, 0)

        elif opcode == "HLT":
            self.require_operands(opcode, operands, 0)
            self.halted = True

        else:
            raise ValueError(f"Unsupported instruction: {opcode}")

        self.history.append({
            "ip": current_ip,
            "instruction": instruction,
            "registers": self.registers.copy(),
            "flags": self.flags.copy(),
        })

        if self.ip >= len(self.program):
            self.halted = True

        return instruction

    def run(self, max_steps=1000):
        steps = 0

        while not self.halted:
            if steps >= max_steps:
                raise RuntimeError(
                    "Execution limit reached. Check for an infinite loop."
                )
            self.step()
            steps += 1

        return steps
