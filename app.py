
import streamlit as st
from cpu8086 import CPU8086

st.set_page_config(
    page_title="8086 Microprocessor Simulator",
    page_icon="💻",
    layout="wide",
)

DEFAULT_PROGRAM = """; 8086 Demo: Sum from 5 down to 1

MOV AX, 0000H
MOV CX, 0005H

LOOP_START:
ADD AX, CX
DEC CX
CMP CX, 0000H
JNZ LOOP_START

HLT
"""


if "cpu" not in st.session_state:
    st.session_state.cpu = CPU8086()

if "source_code" not in st.session_state:
    st.session_state.source_code = DEFAULT_PROGRAM

if "loaded_source" not in st.session_state:
    st.session_state.loaded_source = None

if "message" not in st.session_state:
    st.session_state.message = ""

cpu = st.session_state.cpu

st.title("💻 8086 Microprocessor Simulator")
st.write(
    "Explore 16-bit registers, arithmetic, flags, "
    "conditional jumps, and instruction execution."
)

with st.sidebar:
    st.header("Simulator Guide")
    st.write("**Instructions**")
    st.code(
        "MOV ADD SUB INC DEC CMP\n"
        "AND OR XOR\n"
        "JMP JZ JE JNZ JNE JC JNC\n"
        "NOP HLT"
    )

    st.write("**Registers**")
    st.code("AX BX CX DX SP BP SI DI")

    st.info(
        "Educational simulator for a selected subset "
        "of the 8086 instruction set."
    )

left, right = st.columns([1.2, 1])

with left:
    st.subheader("Assembly Editor")

    source = st.text_area(
        "Write your assembly program",
        value=st.session_state.source_code,
        height=350,
        key="assembly_editor",
    )

    st.session_state.source_code = source

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        load_clicked = st.button("Load", use_container_width=True)

    with c2:
        step_clicked = st.button("Step", use_container_width=True)

    with c3:
        run_clicked = st.button("Run", use_container_width=True)

    with c4:
        reset_clicked = st.button("Reset", use_container_width=True)


def load_program():
    cpu.reset()
    cpu.load_program(st.session_state.source_code)
    st.session_state.loaded_source = st.session_state.source_code


if load_clicked:
    try:
        load_program()
        st.session_state.message = "Program loaded successfully."
    except Exception as exc:
        st.session_state.message = f"ERROR: {exc}"


if step_clicked:
    try:
        if st.session_state.loaded_source != st.session_state.source_code:
            load_program()

        result = cpu.step()
        st.session_state.message = f"Executed: {result}"

    except Exception as exc:
        st.session_state.message = f"ERROR: {exc}"


if run_clicked:
    try:
        if st.session_state.loaded_source != st.session_state.source_code:
            load_program()

        steps = cpu.run(max_steps=1000)
        st.session_state.message = f"Program completed in {steps} step(s)."

    except Exception as exc:
        st.session_state.message = f"ERROR: {exc}"


if reset_clicked:
    try:
        load_program()
        st.session_state.message = "Processor reset and program reloaded."
    except Exception as exc:
        st.session_state.message = f"ERROR: {exc}"


with right:
    st.subheader("CPU State")
    st.write("**Registers (hexadecimal)**")

    names = ["AX", "BX", "CX", "DX", "SP", "BP", "SI", "DI"]

    for start in range(0, len(names), 4):
        columns = st.columns(4)

        for col, name in zip(columns, names[start:start + 4]):
            col.metric(name, f"{cpu.registers[name]:04X}H")

    st.write("**Processor Flags**")
    columns = st.columns(4)

    for col, name in zip(columns, ["CF", "ZF", "SF", "OF"]):
        col.metric(name, cpu.flags[name])

    st.metric("Instruction Pointer (simulated index)", cpu.ip)

    if cpu.halted:
        st.success("CPU status: HALTED")
    else:
        st.info("CPU status: READY")


if st.session_state.message:
    if st.session_state.message.startswith("ERROR"):
        st.error(st.session_state.message)
    else:
        st.success(st.session_state.message)


st.divider()
st.subheader("Execution History")

if cpu.history:
    rows = []

    for entry in cpu.history:
        row = {
            "IP": entry["ip"],
            "Instruction": entry["instruction"],
        }

        for name in names:
            row[name] = f"{entry['registers'][name]:04X}H"

        for name in ["CF", "ZF", "SF", "OF"]:
            row[name] = entry["flags"][name]

        rows.append(row)

    st.dataframe(rows, use_container_width=True, hide_index=True)
else:
    st.write("No instructions executed yet. Click Load, Step, or Run.")


st.divider()
st.subheader("Example Programs")

with st.expander("Addition example"):
    st.code(
        "MOV AX, 0005H\n"
        "MOV BX, 0003H\n"
        "ADD AX, BX\n"
        "HLT",
        language="asm",
    )
    st.write("Expected result: AX = 0008H")

with st.expander("Carry flag example"):
    st.code(
        "MOV AX, FFFFH\n"
        "ADD AX, 0001H\n"
        "HLT",
        language="asm",
    )
    st.write("Expected result: AX = 0000H, CF = 1, ZF = 1")

st.caption(
    "Built with Python and Streamlit | "
    "Educational 8086 instruction simulator"
)
