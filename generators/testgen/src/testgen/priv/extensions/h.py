##################################
# priv/extensions/h.py
#
# H privileged extension test generator.
# nchulani@g.hmc.edu Feb 2026
# SPDX-License-Identifier: Apache-2.0
##################################

"""H privileged extension test generator."""

from testgen.asm.csr import gen_csr_read_sigupd, gen_csr_write_sigupd
from testgen.asm.helpers import comment_banner
from testgen.data.state import TestData
from testgen.priv.registry import add_priv_test_generator


def _generate_hcsr_smoke_tests(test_data: TestData) -> list[str]:
    """Generate a minimal H CSR smoke test expected to pass on current RTL."""
    covergroup = "H_mcsr_cg"
    coverpoint = "cp_hcsr_access"

    # Keep this list intentionally small and limited to CSRs that are
    # hardwired to zero in the current RTL (no WARL/bitmask surprises).
    csrs = [
        "mtinst",
        "mtval2",
    ]

    lines = [
        comment_banner(
            "cp_hcsr_access",
            "Minimal smoke: read a tiny subset of H CSRs expected to be zero in current RTL",
        )
    ]

    check_reg = test_data.int_regs.get_register(exclude_regs=[0])
    for csr in csrs:
        lines.extend(
            [
                test_data.add_testcase(coverpoint, f"{csr}_read", covergroup),
                gen_csr_read_sigupd(check_reg, csr, test_data),
            ]
        )
    test_data.int_regs.return_registers([check_reg])

    return lines


def _generate_hcsr_regression_tests(test_data: TestData) -> list[str]:
    """Generate a small set of H CSR access tests that previously failed."""
    covergroup = "H_mcsr_cg"
    coverpoint = "cp_hcsr_access"

    # Targeted re-introduction of known-problem CSRs.
    csrs = [
        "hedeleg",
        "hvip",
    ]

    save_reg, write_reg = test_data.int_regs.get_registers(2, exclude_regs=[0])
    lines = [
        comment_banner(
            "cp_hcsr_access",
            "Targeted H CSR tests: write all 1s to hedeleg/hvip and read back",
        )
    ]

    for csr in csrs:
        lines.extend(
            [
                f"\tCSRR(x{save_reg}, {csr})      # save {csr}",
                f"\tli x{write_reg}, -1           # all 1s",
                test_data.add_testcase(coverpoint, f"{csr}_writeall1s", covergroup),
                gen_csr_write_sigupd(write_reg, csr, test_data),
                f"\tCSRW({csr}, x{save_reg})      # restore {csr}",
                "",
            ]
        )

    test_data.int_regs.return_registers([save_reg, write_reg])
    return lines


def _generate_hcsr_safe_subset_tests(test_data: TestData) -> list[str]:
    """Generate a safe subset of H CSR access tests aligned with the testplan."""
    covergroup = "H_mcsr_cg"
    coverpoint = "cp_hcsr_access"

    # These CSRs are already implemented with correct masks and should pass
    # write-all-1s tests in the current RTL.
    csrs = [
        "hideleg",
        "vsip",
    ]

    save_reg, write_reg = test_data.int_regs.get_registers(2, exclude_regs=[0])
    lines = [
        comment_banner(
            "cp_hcsr_access",
            "Testplan safe subset: write all 1s to hideleg/vsip and read back",
        )
    ]

    for csr in csrs:
        lines.extend(
            [
                f"\tCSRR(x{save_reg}, {csr})      # save {csr}",
                f"\tli x{write_reg}, -1           # all 1s",
                test_data.add_testcase(coverpoint, f"{csr}_writeall1s", covergroup),
                gen_csr_write_sigupd(write_reg, csr, test_data),
                f"\tCSRW({csr}, x{save_reg})      # restore {csr}",
                "",
            ]
        )

    test_data.int_regs.return_registers([save_reg, write_reg])
    return lines


def _generate_hcsr_safe_readonly_tests(test_data: TestData) -> list[str]:
    """Generate safe read-only checks for read-only CSRs."""
    covergroup = "H_mcsr_cg"
    coverpoint = "cp_hcsr_access"

    csrs = [
        "hip",
        "hgeip",
    ]

    check_reg = test_data.int_regs.get_register(exclude_regs=[0])
    lines = [
        comment_banner(
            "cp_hcsr_access",
            "Testplan safe subset: read-only checks for hip/hgeip",
        )
    ]

    for csr in csrs:
        lines.extend(
            [
                test_data.add_testcase(coverpoint, f"{csr}_read", covergroup),
                gen_csr_read_sigupd(check_reg, csr, test_data),
            ]
        )

    test_data.int_regs.return_registers([check_reg])
    return lines


def _generate_hcsr_expected_fail_tests(test_data: TestData) -> list[str]:
    """Generate a testplan CSR access expected to fail until RTL is fixed."""
    covergroup = "H_mcsr_cg"
    coverpoint = "cp_hcsr_access"

    csrs = [
        "hie",
        "hstatus",
    ]

    save_reg, write_reg = test_data.int_regs.get_registers(2, exclude_regs=[0])
    lines = [
        comment_banner(
            "cp_hcsr_access",
            "Testplan add-on: write-all-1s expected to fail until RTL masks WARL bits",
        ),
    ]

    for csr in csrs:
        lines.extend(
            [
                f"\tCSRR(x{save_reg}, {csr})      # save {csr}",
                f"\tli x{write_reg}, -1           # all 1s",
                test_data.add_testcase(coverpoint, f"{csr}_writeall1s", covergroup),
                gen_csr_write_sigupd(write_reg, csr, test_data),
                f"\tCSRW({csr}, x{save_reg})      # restore {csr}",
                "",
            ]
        )

    test_data.int_regs.return_registers([save_reg, write_reg])
    return lines


def _generate_hcsr_additional_access_tests(test_data: TestData) -> list[str]:
    """Generate additional cp_hcsr_access cases expected to pass on current RTL."""
    covergroup = "H_mcsr_cg"
    coverpoint = "cp_hcsr_access"

    # Additional CSRs from the testplan that should be safe on current RTL.
    csrs = [
        "hcounteren",
        "htimedelta",
        "htval",
        "htinst",
        "vsie",
        "vsscratch",
        "vsepc",
        "vstval",
        "vstvec",
        "vstimecmp",
    ]

    save_reg, write_reg = test_data.int_regs.get_registers(2, exclude_regs=[0])
    lines = [
        comment_banner(
            "cp_hcsr_access",
            "Testplan add-on: write all 1s to additional H/VS CSRs and read back",
        )
    ]

    for csr in csrs:
        lines.extend(
            [
                f"\tCSRR(x{save_reg}, {csr})      # save {csr}",
                f"\tli x{write_reg}, -1           # all 1s",
                test_data.add_testcase(coverpoint, f"{csr}_writeall1s", covergroup),
                gen_csr_write_sigupd(write_reg, csr, test_data),
                f"\tCSRW({csr}, x{save_reg})      # restore {csr}",
                "",
            ]
        )

    test_data.int_regs.return_registers([save_reg, write_reg])
    return lines


def _generate_hcsr_rv32_access_tests(test_data: TestData) -> list[str]:
    """Generate RV32-only cp_hcsr_access cases from the testplan."""
    covergroup = "H_mcsr_cg"
    coverpoint = "cp_hcsr_access"

    # High-half CSRs only exist when XLEN=32.
    csrs = [
        "hedelegh",
        "htimedeltah",
        "vstimecmph",
    ]

    save_reg, write_reg = test_data.int_regs.get_registers(2, exclude_regs=[0])
    lines = [
        comment_banner(
            "cp_hcsr_access",
            "Testplan RV32-only add-on: write all 1s to high-half CSRs and read back",
        ),
        "#if __riscv_xlen == 32",
    ]

    for csr in csrs:
        lines.extend(
            [
                f"\tCSRR(x{save_reg}, {csr})      # save {csr}",
                f"\tli x{write_reg}, -1           # all 1s",
                test_data.add_testcase(coverpoint, f"{csr}_writeall1s", covergroup),
                gen_csr_write_sigupd(write_reg, csr, test_data),
                f"\tCSRW({csr}, x{save_reg})      # restore {csr}",
                "",
            ]
        )

    lines.append("#endif")
    test_data.int_regs.return_registers([save_reg, write_reg])
    return lines


@add_priv_test_generator("H", extensions=["H"])
def make_h(test_data: TestData) -> list[str]:
    """Generate tests for H hypervisor extension."""
    lines: list[str] = []

    # Not in testplan: minimal smoke reads to keep flow green on current RTL.
    lines.extend(_generate_hcsr_smoke_tests(test_data))

    # From testplan (H_mcsr_cg.cp_hcsr_access): targeted failing CSRs now fixed in RTL.
    lines.extend(_generate_hcsr_regression_tests(test_data))

    # From testplan (H_mcsr_cg.cp_hcsr_access): safe subset (write-all-1s on masked CSRs).
    lines.extend(_generate_hcsr_safe_subset_tests(test_data))

    # From testplan (H_mcsr_cg.cp_hcsr_access): read-only checks for hip/hgeip.
    lines.extend(_generate_hcsr_safe_readonly_tests(test_data))

    # From testplan (H_mcsr_cg.cp_hcsr_access): expected-to-fail until RTL masks WARL bits.
    lines.extend(_generate_hcsr_expected_fail_tests(test_data))

    # From testplan (H_mcsr_cg.cp_hcsr_access): additional CSRs expected to pass on current RTL.
    lines.extend(_generate_hcsr_additional_access_tests(test_data))

    # From testplan (H_mcsr_cg.cp_hcsr_access): RV32-only high-half CSRs.
    lines.extend(_generate_hcsr_rv32_access_tests(test_data))

    return lines
