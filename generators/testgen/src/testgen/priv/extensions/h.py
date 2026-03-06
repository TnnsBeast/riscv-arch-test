##################################
# priv/extensions/h.py
#
# H privileged extension test generator.
# nchulani@g.hmc.edu Feb 2026
# SPDX-License-Identifier: Apache-2.0
##################################

"""H privileged extension test generator."""

from testgen.asm.csr import csr_access_test, csr_walk_test, gen_csr_read_sigupd, gen_csr_write_sigupd
from testgen.asm.helpers import comment_banner
from testgen.data.state import TestData
from testgen.priv.registry import add_priv_test_generator

######################################
# CSR groups from Hypervisor - H - US
######################################

# Machine H-extension CSRs
MACHINE_H_CSRS = ["mtinst", "mtval2"]

# HS H-extension CSRs
HS_H_RW_CSRS = [
    "hstatus",
    "hedeleg",
    "hideleg",
    "hie",
    "htimedelta",
    "hcounteren",
    "hgeie",
    "henvcfg",
    "htval",
    "hvip",
    "htinst",
    "hgatp",
]
HS_H_RO_CSRS = ["hip", "hgeip"]
HS_H_RV32_HIGH_CSRS = ["hedelegh", "htimedeltah", "henvcfgh"]

# VS H-extension CSRs
VS_H_RW_CSRS = [
    "vsstatus",
    "vsie",
    "vstval",
    "vsip",
    "vstvec",
    "vsscratch",
    "vsepc",
    "vscause",
    "vsatp",
]

# S CSRs with and without VS replicas
S_VS_REPLICA_PAIRS = [
    ("sstatus", "vsstatus"),
    ("sie", "vsie"),
    ("stvec", "vstvec"),
    ("sscratch", "vsscratch"),
    ("sepc", "vsepc"),
    ("scause", "vscause"),
    ("stval", "vstval"),
    ("sip", "vsip"),
    ("satp", "vsatp"),
]
S_CSR_REPLICA = [s_csr for s_csr, _ in S_VS_REPLICA_PAIRS]
S_CSR_NONREPLICA = ["scounteren", "senvcfg", "scountinhibit"]

# RV64-only illegal high-half CSRs
RV64_H_UPPER_CSRS = ["hedelegh", "htimedeltah", "henvcfgh", "vstimecmph"]

HS_H_WALK_CSRS = [csr for csr in HS_H_RW_CSRS if csr != "hstatus"]
VS_H_WALK_CSRS = [csr for csr in VS_H_RW_CSRS if csr != "vsstatus"]
M_H_WALK_CSRS = MACHINE_H_CSRS + HS_H_WALK_CSRS + VS_H_WALK_CSRS

ALL_BASE_H_CSRS = MACHINE_H_CSRS + HS_H_RW_CSRS + HS_H_RO_CSRS + VS_H_RW_CSRS
ALL_S_CSRS = S_CSR_REPLICA + S_CSR_NONREPLICA


def _emit_readonly_csr_reads(
    test_data: TestData,
    csrs: list[str],
    covergroup: str,
    coverpoint: str,
) -> list[str]:
    """Emit read-only CSR read tests."""
    check_reg = test_data.int_regs.get_register(exclude_regs=[0])
    lines: list[str] = []
    for csr in csrs:
        lines.extend(
            [
                test_data.add_testcase(f"{csr}_read", coverpoint, covergroup),
                f"test_{test_data.test_count}:",
                gen_csr_read_sigupd(check_reg, csr, test_data),
            ]
        )
    test_data.int_regs.return_registers([check_reg])
    return lines


def _emit_faulting_csr_ops(
    test_data: TestData,
    csrs: list[str],
    covergroup: str,
    coverpoint: str,
) -> list[str]:
    """Emit csrw/csrs/csrc/csrr accesses expected to fault."""
    value_reg, read_reg = test_data.int_regs.get_registers(2, exclude_regs=[0])
    lines: list[str] = [f"\tLI(x{value_reg}, -1)      # all 1s for CSR write/set/clear"]

    for csr in csrs:
        lines.extend(
            [
                test_data.add_testcase(f"{csr}_write", coverpoint, covergroup),
                f"test_{test_data.test_count}:",
                f"\tCSRW({csr}, x{value_reg})    # expected trap",
                test_data.add_testcase(f"{csr}_set", coverpoint, covergroup),
                f"test_{test_data.test_count}:",
                f"\tCSRS({csr}, x{value_reg})    # expected trap",
                test_data.add_testcase(f"{csr}_clear", coverpoint, covergroup),
                f"test_{test_data.test_count}:",
                f"\tCSRC({csr}, x{value_reg})    # expected trap",
                test_data.add_testcase(f"{csr}_read", coverpoint, covergroup),
                f"test_{test_data.test_count}:",
                f"\tCSRR(x{read_reg}, {csr})     # expected trap",
                "",
            ]
        )

    test_data.int_regs.return_registers([value_reg, read_reg])
    return lines


def _generate_cp_hcsr_access(
    test_data: TestData,
    covergroup: str,
    description: str,
    writable_csrs: list[str],
    readonly_csrs: list[str],
    mode: str | None = None,
    rv32_csrs: list[str] | None = None,
) -> list[str]:
    """Generate cp_hcsr_access for a covergroup."""
    coverpoint = "cp_hcsr_access"
    lines = [comment_banner(coverpoint, description)]

    if mode is not None:
        lines.append(f"\tRVTEST_GOTO_LOWER_MODE {mode}")

    for csr in writable_csrs:
        lines.extend(csr_access_test(test_data, csr, covergroup, coverpoint))

    lines.extend(_emit_readonly_csr_reads(test_data, readonly_csrs, covergroup, coverpoint))

    if rv32_csrs:
        lines.extend(["#if __riscv_xlen == 32"])
        for csr in rv32_csrs:
            lines.extend(csr_access_test(test_data, csr, covergroup, coverpoint))
        lines.append("#endif")

    if mode is not None:
        lines.append("\tRVTEST_GOTO_MMODE")

    return lines


def _generate_cp_hcsrwalk(
    test_data: TestData,
    covergroup: str,
    description: str,
    walk_csrs: list[str],
    mode: str | None = None,
    rv32_csrs: list[str] | None = None,
) -> list[str]:
    """Generate cp_hcsrwalk for a covergroup."""
    coverpoint = "cp_hcsrwalk"
    lines = [comment_banner(coverpoint, description)]

    if mode is not None:
        lines.append(f"\tRVTEST_GOTO_LOWER_MODE {mode}")

    for csr in walk_csrs:
        lines.extend(csr_walk_test(test_data, csr, covergroup, coverpoint))

    if rv32_csrs:
        lines.extend(["#if __riscv_xlen == 32"])
        for csr in rv32_csrs:
            lines.extend(csr_walk_test(test_data, csr, covergroup, coverpoint))
        lines.append("#endif")

    if mode is not None:
        lines.append("\tRVTEST_GOTO_MMODE")

    return lines


def _generate_fault_matrix_mode(
    test_data: TestData,
    covergroup: str,
    coverpoint: str,
    description: str,
    mode: str,
    csrs: list[str],
    rv32_csrs: list[str] | None = None,
) -> list[str]:
    """Generate faulting CSR accesses in the specified mode."""
    lines = [comment_banner(coverpoint, description), f"\tRVTEST_GOTO_LOWER_MODE {mode}"]
    lines.extend(_emit_faulting_csr_ops(test_data, csrs, covergroup, coverpoint))

    if rv32_csrs:
        lines.extend(["#if __riscv_xlen == 32"])
        lines.extend(_emit_faulting_csr_ops(test_data, rv32_csrs, covergroup, coverpoint))
        lines.append("#endif")

    lines.append("\tRVTEST_GOTO_MMODE")
    return lines


def _generate_illegalupper_mode(
    test_data: TestData,
    covergroup: str,
    mode: str,
) -> list[str]:
    """Generate cp_illegalupper in the specified mode."""
    coverpoint = "cp_illegalupper"
    lines = [
        comment_banner(
            coverpoint,
            "RV64 only: h-half CSRs are illegal from this mode",
        ),
        f"\tRVTEST_GOTO_LOWER_MODE {mode}",
        "#if __riscv_xlen == 64",
    ]
    lines.extend(_emit_faulting_csr_ops(test_data, RV64_H_UPPER_CSRS, covergroup, coverpoint))
    lines.extend(
        [
            "#endif",
            "\tRVTEST_GOTO_MMODE",
        ]
    )
    return lines


def _generate_cp_replica_independent(
    test_data: TestData,
    covergroup: str,
    description: str,
    mode: str | None = None,
) -> list[str]:
    """Generate cp_replica where S and VS CSR writes remain independent."""
    coverpoint = "cp_replica"
    save_s_reg, save_vs_reg, write_reg, check_reg = test_data.int_regs.get_registers(4, exclude_regs=[0])

    lines = [comment_banner(coverpoint, description)]
    if mode is not None:
        lines.append(f"\tRVTEST_GOTO_LOWER_MODE {mode}")

    for idx, (s_csr, vs_csr) in enumerate(S_VS_REPLICA_PAIRS):
        s_value = 0 if s_csr == "satp" else 0x110 + idx
        vs_value = 0 if s_csr == "satp" else 0x220 + idx

        lines.extend(
            [
                f"\tCSRR(x{save_s_reg}, {s_csr})      # save {s_csr}",
                f"\tCSRR(x{save_vs_reg}, {vs_csr})    # save {vs_csr}",
                f"\tLI(x{write_reg}, 0x{s_value:08x})",
                test_data.add_testcase(f"{s_csr}_write", coverpoint, covergroup),
                f"test_{test_data.test_count}:",
                gen_csr_write_sigupd(write_reg, s_csr, test_data),
                f"\tLI(x{write_reg}, 0x{vs_value:08x})",
                test_data.add_testcase(f"{vs_csr}_write", coverpoint, covergroup),
                f"test_{test_data.test_count}:",
                gen_csr_write_sigupd(write_reg, vs_csr, test_data),
                test_data.add_testcase(f"{s_csr}_read", coverpoint, covergroup),
                f"test_{test_data.test_count}:",
                gen_csr_read_sigupd(check_reg, s_csr, test_data),
                test_data.add_testcase(f"{vs_csr}_read", coverpoint, covergroup),
                f"test_{test_data.test_count}:",
                gen_csr_read_sigupd(check_reg, vs_csr, test_data),
                f"\tCSRW({s_csr}, x{save_s_reg})      # restore {s_csr}",
                f"\tCSRW({vs_csr}, x{save_vs_reg})    # restore {vs_csr}",
                "",
            ]
        )

    if mode is not None:
        lines.append("\tRVTEST_GOTO_MMODE")

    test_data.int_regs.return_registers([save_s_reg, save_vs_reg, write_reg, check_reg])
    return lines


def _generate_h_mcsr_cp_hcsr_access(test_data: TestData) -> list[str]:
    """H_mcsr_cg / cp_hcsr_access."""
    covergroup = "H_mcsr_cg"
    writable_csrs = MACHINE_H_CSRS + HS_H_RW_CSRS + VS_H_RW_CSRS
    return _generate_cp_hcsr_access(
        test_data,
        covergroup,
        "Tests executed in M-mode: all Machine/HS/VS H-extension CSR accesses",
        writable_csrs,
        HS_H_RO_CSRS,
        rv32_csrs=HS_H_RV32_HIGH_CSRS,
    )


def _generate_h_mcsr_cp_hcsrwalk(test_data: TestData) -> list[str]:
    """H_mcsr_cg / cp_hcsrwalk."""
    return _generate_cp_hcsrwalk(
        test_data,
        "H_mcsr_cg",
        "Tests executed in M-mode: walk each writable H-extension CSR bit",
        M_H_WALK_CSRS,
        rv32_csrs=HS_H_RV32_HIGH_CSRS,
    )


def _generate_h_mcsr_cp_replica(test_data: TestData) -> list[str]:
    """H_mcsr_cg / cp_replica."""
    return _generate_cp_replica_independent(
        test_data,
        "H_mcsr_cg",
        "In M-mode, writing S/VS CSR pairs should not affect the replica counterpart",
    )


def _generate_h_mcsr_cp_mtvala(test_data: TestData) -> list[str]:
    """H_mcsr_cg / cp_mtvala."""
    covergroup = "H_mcsr_cg"
    coverpoint = "cp_mtvala"
    save_reg, write_reg, check_reg = test_data.int_regs.get_registers(3, exclude_regs=[0])

    lines = [
        comment_banner(
            coverpoint,
            "Write all 1s to mtval and read back",
        ),
        f"\tCSRR(x{save_reg}, mtval)      # save mtval",
        f"\tLI(x{write_reg}, -1)",
        test_data.add_testcase("writeall1s", coverpoint, covergroup),
        f"test_{test_data.test_count}:",
        gen_csr_write_sigupd(write_reg, "mtval", test_data),
        test_data.add_testcase("read", coverpoint, covergroup),
        f"test_{test_data.test_count}:",
        gen_csr_read_sigupd(check_reg, "mtval", test_data),
        f"\tCSRW(mtval, x{save_reg})      # restore mtval",
    ]

    test_data.int_regs.return_registers([save_reg, write_reg, check_reg])
    return lines


def _generate_h_hscsr_cp_hcsr_access(test_data: TestData) -> list[str]:
    """H_hscsr_cg / cp_hcsr_access."""
    covergroup = "H_hscsr_cg"
    writable_csrs = HS_H_RW_CSRS + VS_H_RW_CSRS
    return _generate_cp_hcsr_access(
        test_data,
        covergroup,
        "Tests executed in HS-mode: HS/VS H-extension CSR accesses",
        writable_csrs,
        HS_H_RO_CSRS,
        mode="HSmode",
        rv32_csrs=HS_H_RV32_HIGH_CSRS,
    )


def _generate_h_hscsr_cp_hcsrwalk(test_data: TestData) -> list[str]:
    """H_hscsr_cg / cp_hcsrwalk."""
    return _generate_cp_hcsrwalk(
        test_data,
        "H_hscsr_cg",
        "Tests executed in HS-mode: walk writable HS/VS H-extension CSR bits (excluding hstatus/vsstatus)",
        HS_H_WALK_CSRS + VS_H_WALK_CSRS,
        mode="HSmode",
        rv32_csrs=HS_H_RV32_HIGH_CSRS,
    )


def _generate_h_hscsr_cp_hcsr_inaccessible(test_data: TestData) -> list[str]:
    """H_hscsr_cg / cp_hcsr_inaccessible."""
    return _generate_fault_matrix_mode(
        test_data,
        "H_hscsr_cg",
        "cp_hcsr_inaccessible",
        "In HS-mode, machine H-extension CSRs are inaccessible",
        "HSmode",
        MACHINE_H_CSRS,
    )


def _generate_h_hscsr_cp_replica(test_data: TestData) -> list[str]:
    """H_hscsr_cg / cp_replica."""
    return _generate_cp_replica_independent(
        test_data,
        "H_hscsr_cg",
        "In HS-mode, writing S/VS CSR pairs should not affect the replica counterpart",
        mode="HSmode",
    )


def _generate_h_hscsr_cp_hstatus_vgein(test_data: TestData) -> list[str]:
    """H_hscsr_cg / cp_hstatus_vgein."""
    covergroup = "H_hscsr_cg"
    coverpoint = "cp_hstatus_vgein"
    save_reg, base_reg, mask_reg, value_reg = test_data.int_regs.get_registers(4, exclude_regs=[0])

    # Current RTL hardwires GEILEN=0, so GEILEN-relative values collapse to {0,1,63}.
    test_values = [
        ("vgein_0", 0),
        ("vgein_1", 1),
        ("vgein_geilen_m1", 63),
        ("vgein_geilen", 0),
        ("vgein_geilen_p1", 1),
        ("vgein_63", 63),
    ]

    lines = [
        comment_banner(
            coverpoint,
            "In HS-mode, write {0,1,GEILEN-1,GEILEN,GEILEN+1,63} to hstatus.VGEIN",
        ),
        "\tRVTEST_GOTO_LOWER_MODE HSmode",
        f"\tCSRR(x{save_reg}, hstatus)      # save hstatus",
        f"\tLI(x{mask_reg}, 0x0003f000)     # hstatus.VGEIN mask [17:12]",
        f"\tnot x{mask_reg}, x{mask_reg}",
        f"\tand x{base_reg}, x{save_reg}, x{mask_reg}    # clear VGEIN bits",
    ]

    for bin_name, vgein in test_values:
        lines.extend(
            [
                f"\tLI(x{value_reg}, 0x{(vgein << 12):08x})",
                f"\tor x{value_reg}, x{value_reg}, x{base_reg}",
                test_data.add_testcase(bin_name, coverpoint, covergroup),
                f"test_{test_data.test_count}:",
                gen_csr_write_sigupd(value_reg, "hstatus", test_data),
            ]
        )

    lines.extend(
        [
            f"\tCSRW(hstatus, x{save_reg})      # restore hstatus",
            "\tRVTEST_GOTO_MMODE",
        ]
    )

    test_data.int_regs.return_registers([save_reg, base_reg, mask_reg, value_reg])
    return lines


def _generate_h_hscsr_cp_vscause_write(test_data: TestData) -> list[str]:
    """H_hscsr_cg / cp_vscause_write."""
    covergroup = "H_hscsr_cg"
    coverpoint = "cp_vscause_write"
    save_reg, value_reg, msb_reg = test_data.int_regs.get_registers(3, exclude_regs=[0])

    lines = [
        comment_banner(
            coverpoint,
            "In HS-mode, write vscause values with interrupt=1 (0-15) and interrupt=0 (0-64)",
        ),
        "\tRVTEST_GOTO_LOWER_MODE HSmode",
        f"\tCSRR(x{save_reg}, vscause)      # save vscause",
        f"\tSET_MSB(x{msb_reg})             # interrupt bit",
    ]

    for cause in range(16):
        lines.extend(
            [
                f"\tLI(x{value_reg}, {cause})",
                f"\tor x{value_reg}, x{value_reg}, x{msb_reg}",
                test_data.add_testcase(f"intr_{cause}", coverpoint, covergroup),
                f"test_{test_data.test_count}:",
                gen_csr_write_sigupd(value_reg, "vscause", test_data),
            ]
        )

    for cause in range(65):
        lines.extend(
            [
                f"\tLI(x{value_reg}, {cause})",
                test_data.add_testcase(f"exc_{cause}", coverpoint, covergroup),
                f"test_{test_data.test_count}:",
                gen_csr_write_sigupd(value_reg, "vscause", test_data),
            ]
        )

    lines.extend(
        [
            f"\tCSRW(vscause, x{save_reg})      # restore vscause",
            "\tRVTEST_GOTO_MMODE",
        ]
    )

    test_data.int_regs.return_registers([save_reg, value_reg, msb_reg])
    return lines


def _generate_h_hscsr_cp_tvm(test_data: TestData) -> list[str]:
    """H_hscsr_cg / cp_tvm."""
    covergroup = "H_hscsr_cg"
    coverpoint = "cp_tvm"
    save_mstatus_reg, base_mstatus_reg, mask_reg, value_reg, check_reg = test_data.int_regs.get_registers(
        5, exclude_regs=[0]
    )

    lines = [
        comment_banner(
            coverpoint,
            "In HS-mode, TVM controls satp/hgatp CSR access traps",
        ),
        f"\tCSRR(x{save_mstatus_reg}, mstatus)      # save mstatus",
        f"\tLI(x{mask_reg}, 0x00100000)             # mstatus.TVM bit",
        f"\tnot x{mask_reg}, x{mask_reg}",
        f"\tand x{base_mstatus_reg}, x{save_mstatus_reg}, x{mask_reg}   # clear TVM",
    ]

    for tvm in (0, 1):
        lines.extend(
            [
                f"\tLI(x{value_reg}, 0x{(tvm << 20):08x})",
                f"\tor x{value_reg}, x{value_reg}, x{base_mstatus_reg}",
                f"\tCSRW(mstatus, x{value_reg})",
                "\tRVTEST_GOTO_LOWER_MODE HSmode",
            ]
        )

        if tvm == 0:
            lines.extend(
                [
                    test_data.add_testcase(f"tvm_{tvm}_satp_read", coverpoint, covergroup),
                    f"test_{test_data.test_count}:",
                    gen_csr_read_sigupd(check_reg, "satp", test_data),
                    f"\tLI(x{value_reg}, 0)",  # keep bare mode for safety
                    test_data.add_testcase(f"tvm_{tvm}_satp_write", coverpoint, covergroup),
                    f"test_{test_data.test_count}:",
                    gen_csr_write_sigupd(value_reg, "satp", test_data),
                    test_data.add_testcase(f"tvm_{tvm}_hgatp_read", coverpoint, covergroup),
                    f"test_{test_data.test_count}:",
                    gen_csr_read_sigupd(check_reg, "hgatp", test_data),
                    f"\tLI(x{value_reg}, 0)",
                    test_data.add_testcase(f"tvm_{tvm}_hgatp_write", coverpoint, covergroup),
                    f"test_{test_data.test_count}:",
                    gen_csr_write_sigupd(value_reg, "hgatp", test_data),
                ]
            )
        else:
            lines.extend(
                [
                    test_data.add_testcase(f"tvm_{tvm}_satp_read", coverpoint, covergroup),
                    f"test_{test_data.test_count}:",
                    f"\tCSRR(x{check_reg}, satp)     # expected trap",
                    f"\tLI(x{value_reg}, 0)",
                    test_data.add_testcase(f"tvm_{tvm}_satp_write", coverpoint, covergroup),
                    f"test_{test_data.test_count}:",
                    f"\tCSRW(satp, x{value_reg})     # expected trap",
                    test_data.add_testcase(f"tvm_{tvm}_hgatp_read", coverpoint, covergroup),
                    f"test_{test_data.test_count}:",
                    f"\tCSRR(x{check_reg}, hgatp)    # expected trap",
                    f"\tLI(x{value_reg}, 0)",
                    test_data.add_testcase(f"tvm_{tvm}_hgatp_write", coverpoint, covergroup),
                    f"test_{test_data.test_count}:",
                    f"\tCSRW(hgatp, x{value_reg})    # expected trap",
                ]
            )

        lines.append("\tRVTEST_GOTO_MMODE")

    lines.append(f"\tCSRW(mstatus, x{save_mstatus_reg})      # restore mstatus")
    test_data.int_regs.return_registers([save_mstatus_reg, base_mstatus_reg, mask_reg, value_reg, check_reg])
    return lines


def _generate_h_vscsr_cp_hcsr_inaccessible(test_data: TestData) -> list[str]:
    """H_vscsr_cg / cp_hcsr_inaccessible."""
    return _generate_fault_matrix_mode(
        test_data,
        "H_vscsr_cg",
        "cp_hcsr_inaccessible",
        "In VS-mode, machine H-extension CSRs are inaccessible",
        "VSmode",
        MACHINE_H_CSRS,
    )


def _generate_h_vscsr_cp_hcsr_virtualinstructionfault(test_data: TestData) -> list[str]:
    """H_vscsr_cg / cp_hcsr_virtualinstructionfault."""
    covergroup = "H_vscsr_cg"
    coverpoint = "cp_hcsr_virtualinstructionfault"
    hs_vs_csrs = HS_H_RW_CSRS + HS_H_RO_CSRS + VS_H_RW_CSRS

    return _generate_fault_matrix_mode(
        test_data,
        covergroup,
        coverpoint,
        "In VS-mode, accesses to HS/VS H-extension CSRs cause virtual-instruction fault",
        "VSmode",
        hs_vs_csrs,
    )


def _generate_h_vscsr_cp_illegalupper(test_data: TestData) -> list[str]:
    """H_vscsr_cg / cp_illegalupper."""
    return _generate_illegalupper_mode(test_data, "H_vscsr_cg", "VSmode")


def _generate_h_vscsr_cp_replica(test_data: TestData) -> list[str]:
    """H_vscsr_cg / cp_replica."""
    covergroup = "H_vscsr_cg"
    coverpoint = "cp_replica"
    save_s_reg, save_vs_reg, write_reg, check_reg = test_data.int_regs.get_registers(4, exclude_regs=[0])

    lines = [
        comment_banner(
            coverpoint,
            "In VS-mode, S CSR accesses affect VS replicas",
        )
    ]

    for idx, (s_csr, vs_csr) in enumerate(S_VS_REPLICA_PAIRS):
        write_value = 0 if s_csr == "satp" else 0x330 + idx
        lines.extend(
            [
                f"\tCSRR(x{save_s_reg}, {s_csr})      # save {s_csr}",
                f"\tCSRR(x{save_vs_reg}, {vs_csr})    # save {vs_csr}",
                "\tRVTEST_GOTO_LOWER_MODE VSmode",
                f"\tLI(x{write_reg}, 0x{write_value:08x})",
                test_data.add_testcase(f"{s_csr}_write_vs", coverpoint, covergroup),
                f"test_{test_data.test_count}:",
                gen_csr_write_sigupd(write_reg, s_csr, test_data),
                test_data.add_testcase(f"{s_csr}_read_vs", coverpoint, covergroup),
                f"test_{test_data.test_count}:",
                gen_csr_read_sigupd(check_reg, s_csr, test_data),
                "\tRVTEST_GOTO_MMODE",
                test_data.add_testcase(f"{s_csr}_read_m", coverpoint, covergroup),
                f"test_{test_data.test_count}:",
                gen_csr_read_sigupd(check_reg, s_csr, test_data),
                test_data.add_testcase(f"{vs_csr}_read_m", coverpoint, covergroup),
                f"test_{test_data.test_count}:",
                gen_csr_read_sigupd(check_reg, vs_csr, test_data),
                f"\tCSRW({s_csr}, x{save_s_reg})      # restore {s_csr}",
                f"\tCSRW({vs_csr}, x{save_vs_reg})    # restore {vs_csr}",
                "",
            ]
        )

    test_data.int_regs.return_registers([save_s_reg, save_vs_reg, write_reg, check_reg])
    return lines


def _generate_h_vscsr_cp_nonreplica(test_data: TestData) -> list[str]:
    """H_vscsr_cg / cp_nonreplica."""
    covergroup = "H_vscsr_cg"
    coverpoint = "cp_nonreplica"
    lines = [
        comment_banner(
            coverpoint,
            "In VS-mode, accesses to nonreplicated S CSRs behave normally",
        ),
        "\tRVTEST_GOTO_LOWER_MODE VSmode",
    ]

    for csr in S_CSR_NONREPLICA:
        lines.extend(csr_access_test(test_data, csr, covergroup, coverpoint))

    lines.append("\tRVTEST_GOTO_MMODE")
    return lines


def _generate_h_vscsr_cp_vsstatus_sd_write(test_data: TestData) -> list[str]:
    """H_vscsr_cg / cp_vsstatus_sd_write."""
    covergroup = "H_vscsr_cg"
    coverpoint = "cp_vsstatus_sd_write"
    save_reg, base_reg, msb_reg, mask_reg, value_reg = test_data.int_regs.get_registers(5, exclude_regs=[0])

    lines = [
        comment_banner(
            coverpoint,
            "In VS-mode, write SD/FS/VS combinations and read back vsstatus",
        ),
        "\tRVTEST_GOTO_LOWER_MODE VSmode",
        f"\tCSRR(x{save_reg}, vsstatus)      # save vsstatus",
        f"\tSET_MSB(x{msb_reg})              # SD bit",
        f"\tnot x{mask_reg}, x{msb_reg}",
        f"\tand x{base_reg}, x{save_reg}, x{mask_reg}    # clear SD",
        f"\tLI(x{mask_reg}, 0x00006600)      # FS [14:13], VS [10:9]",
        f"\tnot x{mask_reg}, x{mask_reg}",
        f"\tand x{base_reg}, x{base_reg}, x{mask_reg}    # clear FS/VS",
    ]

    for sd in (0, 1):
        for fs in range(4):
            for vs in range(4):
                bin_name = f"sd_{sd}_fs_{fs:02b}_vs_{vs:02b}"
                fields = (fs << 13) | (vs << 9)
                lines.extend(
                    [
                        f"\tLI(x{value_reg}, 0x{fields:08x})",
                    ]
                )
                if sd == 1:
                    lines.append(f"\tor x{value_reg}, x{value_reg}, x{msb_reg}    # set SD")
                lines.extend(
                    [
                        f"\tor x{value_reg}, x{value_reg}, x{base_reg}",
                        test_data.add_testcase(bin_name, coverpoint, covergroup),
                        f"test_{test_data.test_count}:",
                        gen_csr_write_sigupd(value_reg, "vsstatus", test_data),
                    ]
                )

    lines.extend(
        [
            f"\tCSRW(vsstatus, x{save_reg})      # restore vsstatus",
            "\tRVTEST_GOTO_MMODE",
        ]
    )

    test_data.int_regs.return_registers([save_reg, base_reg, msb_reg, mask_reg, value_reg])
    return lines


def _generate_h_vscsr_cp_tvm(test_data: TestData) -> list[str]:
    """H_vscsr_cg / cp_tvm."""
    covergroup = "H_vscsr_cg"
    coverpoint = "cp_tvm"
    save_m_reg, base_m_reg, save_h_reg, base_h_reg, mask_reg, value_reg, check_reg = test_data.int_regs.get_registers(
        7, exclude_regs=[0]
    )

    lines = [
        comment_banner(
            coverpoint,
            "In VS-mode, VTVM (not TVM) controls satp trap behavior",
        ),
        f"\tCSRR(x{save_m_reg}, mstatus)      # save mstatus",
        f"\tCSRR(x{save_h_reg}, hstatus)      # save hstatus",
        f"\tLI(x{mask_reg}, 0x00100000)       # TVM/VTVM bit",
        f"\tnot x{mask_reg}, x{mask_reg}",
        f"\tand x{base_m_reg}, x{save_m_reg}, x{mask_reg}   # clear mstatus.TVM",
        f"\tand x{base_h_reg}, x{save_h_reg}, x{mask_reg}   # clear hstatus.VTVM",
    ]

    for tvm in (0, 1):
        for vtvm in (0, 1):
            lines.extend(
                [
                    f"\tLI(x{value_reg}, 0x{(tvm << 20):08x})",
                    f"\tor x{value_reg}, x{value_reg}, x{base_m_reg}",
                    f"\tCSRW(mstatus, x{value_reg})",
                    f"\tLI(x{value_reg}, 0x{(vtvm << 20):08x})",
                    f"\tor x{value_reg}, x{value_reg}, x{base_h_reg}",
                    f"\tCSRW(hstatus, x{value_reg})",
                    "\tRVTEST_GOTO_LOWER_MODE VSmode",
                ]
            )

            if vtvm == 0:
                lines.extend(
                    [
                        test_data.add_testcase(f"tvm_{tvm}_vtvm_{vtvm}_satp_read", coverpoint, covergroup),
                        f"test_{test_data.test_count}:",
                        gen_csr_read_sigupd(check_reg, "satp", test_data),
                        f"\tLI(x{value_reg}, 0)",  # keep bare mode for safety
                        test_data.add_testcase(f"tvm_{tvm}_vtvm_{vtvm}_satp_write", coverpoint, covergroup),
                        f"test_{test_data.test_count}:",
                        gen_csr_write_sigupd(value_reg, "satp", test_data),
                    ]
                )
            else:
                lines.extend(
                    [
                        test_data.add_testcase(f"tvm_{tvm}_vtvm_{vtvm}_satp_read", coverpoint, covergroup),
                        f"test_{test_data.test_count}:",
                        f"\tCSRR(x{check_reg}, satp)     # expected trap",
                        f"\tLI(x{value_reg}, 0)",
                        test_data.add_testcase(f"tvm_{tvm}_vtvm_{vtvm}_satp_write", coverpoint, covergroup),
                        f"test_{test_data.test_count}:",
                        f"\tCSRW(satp, x{value_reg})     # expected trap",
                    ]
                )

            lines.append("\tRVTEST_GOTO_MMODE")

    lines.extend(
        [
            f"\tCSRW(mstatus, x{save_m_reg})      # restore mstatus",
            f"\tCSRW(hstatus, x{save_h_reg})      # restore hstatus",
        ]
    )

    test_data.int_regs.return_registers([save_m_reg, base_m_reg, save_h_reg, base_h_reg, mask_reg, value_reg, check_reg])
    return lines


def _generate_h_ucsr_cp_hcsr_inaccessible(test_data: TestData) -> list[str]:
    """H_ucsr_cg / cp_hcsr_inaccessible."""
    return _generate_fault_matrix_mode(
        test_data,
        "H_ucsr_cg",
        "cp_hcsr_inaccessible",
        "In U-mode, all H-extension CSRs are inaccessible",
        "Umode",
        ALL_BASE_H_CSRS,
        rv32_csrs=HS_H_RV32_HIGH_CSRS,
    )


def _generate_h_ucsr_cp_illegalupper(test_data: TestData) -> list[str]:
    """H_ucsr_cg / cp_illegalupper."""
    return _generate_illegalupper_mode(test_data, "H_ucsr_cg", "Umode")


def _generate_h_ucsr_cp_scsr(test_data: TestData) -> list[str]:
    """H_ucsr_cg / cp_scsr."""
    return _generate_fault_matrix_mode(
        test_data,
        "H_ucsr_cg",
        "cp_scsr",
        "In U-mode, supervisor CSRs (with/without VS replicas) are inaccessible",
        "Umode",
        ALL_S_CSRS,
    )


def _generate_h_vucsr_cp_hcsr_inaccessible(test_data: TestData) -> list[str]:
    """H_vucsr_cg / cp_hcsr_inaccessible."""
    return _generate_fault_matrix_mode(
        test_data,
        "H_vucsr_cg",
        "cp_hcsr_inaccessible",
        "In VU-mode, H-extension CSRs are inaccessible",
        "VUmode",
        ALL_BASE_H_CSRS,
        rv32_csrs=HS_H_RV32_HIGH_CSRS,
    )


def _generate_h_vucsr_cp_illegalupper(test_data: TestData) -> list[str]:
    """H_vucsr_cg / cp_illegalupper."""
    return _generate_illegalupper_mode(test_data, "H_vucsr_cg", "VUmode")


def _generate_h_vucsr_cp_scsr(test_data: TestData) -> list[str]:
    """H_vucsr_cg / cp_scsr."""
    return _generate_fault_matrix_mode(
        test_data,
        "H_vucsr_cg",
        "cp_scsr",
        "In VU-mode, supervisor CSRs (with/without VS replicas) fault",
        "VUmode",
        ALL_S_CSRS,
    )


def _generate_h_mcsr_cg(test_data: TestData) -> list[str]:
    """Generate CSV section: Tests executed in M-mode (H_mcsr_cg)."""
    lines: list[str] = []
    lines.extend(_generate_h_mcsr_cp_hcsr_access(test_data))
    lines.extend(_generate_h_mcsr_cp_hcsrwalk(test_data))
    lines.extend(_generate_h_mcsr_cp_replica(test_data))
    lines.extend(_generate_h_mcsr_cp_mtvala(test_data))
    return lines


def _generate_h_hscsr_cg(test_data: TestData) -> list[str]:
    """Generate CSV section: Tests executed in HS-mode (H_hscsr_cg)."""
    lines: list[str] = []
    lines.extend(_generate_h_hscsr_cp_hcsr_access(test_data))
    lines.extend(_generate_h_hscsr_cp_hcsrwalk(test_data))
    lines.extend(_generate_h_hscsr_cp_hcsr_inaccessible(test_data))
    lines.extend(_generate_h_hscsr_cp_replica(test_data))
    lines.extend(_generate_h_hscsr_cp_hstatus_vgein(test_data))
    lines.extend(_generate_h_hscsr_cp_vscause_write(test_data))
    lines.extend(_generate_h_hscsr_cp_tvm(test_data))
    return lines


def _generate_h_vscsr_cg(test_data: TestData) -> list[str]:
    """Generate CSV section: Tests executed in VS-mode (H_vscsr_cg)."""
    lines: list[str] = []
    lines.extend(_generate_h_vscsr_cp_hcsr_inaccessible(test_data))
    lines.extend(_generate_h_vscsr_cp_hcsr_virtualinstructionfault(test_data))
    lines.extend(_generate_h_vscsr_cp_illegalupper(test_data))
    lines.extend(_generate_h_vscsr_cp_replica(test_data))
    lines.extend(_generate_h_vscsr_cp_nonreplica(test_data))
    lines.extend(_generate_h_vscsr_cp_vsstatus_sd_write(test_data))
    lines.extend(_generate_h_vscsr_cp_tvm(test_data))
    return lines


def _generate_h_ucsr_cg(test_data: TestData) -> list[str]:
    """Generate CSV section: Tests executed in U-mode (H_ucsr_cg)."""
    lines: list[str] = []
    lines.extend(_generate_h_ucsr_cp_hcsr_inaccessible(test_data))
    lines.extend(_generate_h_ucsr_cp_illegalupper(test_data))
    lines.extend(_generate_h_ucsr_cp_scsr(test_data))
    return lines


def _generate_h_vucsr_cg(test_data: TestData) -> list[str]:
    """Generate CSV section: Tests executed in VU-mode (H_vucsr_cg)."""
    lines: list[str] = []
    lines.extend(_generate_h_vucsr_cp_hcsr_inaccessible(test_data))
    lines.extend(_generate_h_vucsr_cp_illegalupper(test_data))
    lines.extend(_generate_h_vucsr_cp_scsr(test_data))
    return lines


@add_priv_test_generator("H", required_extensions=["H"])
def make_h(test_data: TestData) -> list[str]:
    """Generate tests for H hypervisor extension."""
    lines: list[str] = []

    # Hypervisor - H - US
    # CSR covergroups only
    lines.extend(_generate_h_mcsr_cg(test_data))
    lines.extend(_generate_h_hscsr_cg(test_data))
    lines.extend(_generate_h_vscsr_cg(test_data))
    lines.extend(_generate_h_ucsr_cg(test_data))
    lines.extend(_generate_h_vucsr_cg(test_data))

    return lines
