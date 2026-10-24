
from cpu8086 import CPU8086


def run_program(source):
    cpu = CPU8086()
    cpu.load_program(source)
    cpu.run()
    return cpu


def test_addition():
    cpu = run_program("""
        MOV AX, 0005H
        MOV BX, 0003H
        ADD AX, BX
        HLT
    """)
    assert cpu.registers["AX"] == 8


def test_subtraction():
    cpu = run_program("""
        MOV AX, 000AH
        SUB AX, 0003H
        HLT
    """)
    assert cpu.registers["AX"] == 7


def test_carry_flag():
    cpu = run_program("""
        MOV AX, FFFFH
        ADD AX, 0001H
        HLT
    """)
    assert cpu.registers["AX"] == 0
    assert cpu.flags["CF"] == 1
    assert cpu.flags["ZF"] == 1


def test_overflow_flag():
    cpu = run_program("""
        MOV AX, 7FFFH
        ADD AX, 0001H
        HLT
    """)
    assert cpu.registers["AX"] == 0x8000
    assert cpu.flags["OF"] == 1


def test_loop_and_labels():
    cpu = run_program("""
        MOV AX, 0000H
        MOV CX, 0005H

        LOOP_START:
        ADD AX, CX
        DEC CX
        CMP CX, 0000H
        JNZ LOOP_START
        HLT
    """)
    assert cpu.registers["AX"] == 15
    assert cpu.registers["CX"] == 0
