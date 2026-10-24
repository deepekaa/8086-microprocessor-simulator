# 8086 Microprocessor Simulator

An interactive educational simulator for a selected subset of the
Intel 8086 instruction set, built with Python and Streamlit.

## Features

- 16-bit general-purpose and index registers
- Assembly code editor
- Step-by-step instruction execution
- Full-program execution
- Arithmetic and logical instructions
- Labels and conditional jumps
- Carry, Zero, Sign and Overflow flag visualization
- Execution history
- Automated tests for core instructions

## Supported Instructions

MOV, ADD, SUB, INC, DEC, CMP, AND, OR, XOR, JMP, JZ, JE,
JNZ, JNE, JC, JNC, NOP and HLT.

## Technologies

- Python
- Streamlit
- pytest (for automated tests)
- GitHub
- Render

## Run Locally

Install dependencies:

    pip install -r requirements.txt

Run the application:

    streamlit run app.py

Run tests (install pytest first):

    pip install pytest
    python -m pytest -q

## Example

    MOV AX, 0005H
    MOV BX, 0003H
    ADD AX, BX
    HLT

Expected result: AX = 0008H.

## Scope

This is an educational simulator implementing a subset of the
8086 instruction set. It is not a complete or cycle-accurate
Intel 8086 emulator. Segmented memory, 8-bit registers, interrupts,
machine-code encoding and the full instruction set are not yet
implemented.

## Author

Deepekaa K
Electronics & Computer Engineering
