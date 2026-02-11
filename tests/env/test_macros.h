// Extra CSR encodings not yet present in generated encoding.h. for H tests
#ifndef CSR_VSSTATUS
#define CSR_VSSTATUS 0x200
#endif
#ifndef CSR_VSIE
#define CSR_VSIE 0x204
#endif
#ifndef CSR_VSTVEC
#define CSR_VSTVEC 0x205
#endif
#ifndef CSR_VSSCRATCH
#define CSR_VSSCRATCH 0x240
#endif
#ifndef CSR_VSEPC
#define CSR_VSEPC 0x241
#endif
#ifndef CSR_VSCAUSE
#define CSR_VSCAUSE 0x242
#endif
#ifndef CSR_VSTVAL
#define CSR_VSTVAL 0x243
#endif
#ifndef CSR_VSIP
#define CSR_VSIP 0x244
#endif
#ifndef CSR_VSTIMECMP
#define CSR_VSTIMECMP 0x24d
#endif
#ifndef CSR_VSTIMECMPH
#define CSR_VSTIMECMPH 0x25d
#endif
#ifndef CSR_VSATP
#define CSR_VSATP 0x280
#endif
#ifndef CSR_MTINST
#define CSR_MTINST 0x34a
#endif
#ifndef CSR_MTVAL2
#define CSR_MTVAL2 0x34b
#endif
#ifndef CSR_HSTATUS
#define CSR_HSTATUS 0x600
#endif
#ifndef CSR_HEDELEG
#define CSR_HEDELEG 0x602
#endif
#ifndef CSR_VEDELEG
#define CSR_VEDELEG CSR_HEDELEG
#endif
#ifndef CSR_HIDELEG
#define CSR_HIDELEG 0x603
#endif
#ifndef CSR_HIE
#define CSR_HIE 0x604
#endif
#ifndef CSR_HTIMEDELTA
#define CSR_HTIMEDELTA 0x605
#endif
#ifndef CSR_HCOUNTEREN
#define CSR_HCOUNTEREN 0x606
#endif
#ifndef CSR_HGEIE
#define CSR_HGEIE 0x607
#endif
#ifndef CSR_HENVCFG
#define CSR_HENVCFG 0x60a
#endif
#ifndef CSR_HEDELEGH
#define CSR_HEDELEGH 0x612
#endif
#ifndef CSR_HTIMEDELTAH
#define CSR_HTIMEDELTAH 0x615
#endif
#ifndef CSR_HENVCFGH
#define CSR_HENVCFGH 0x61a
#endif
#ifndef CSR_HTVAL
#define CSR_HTVAL 0x643
#endif
#ifndef CSR_HIP
#define CSR_HIP 0x644
#endif
#ifndef CSR_HVIP
#define CSR_HVIP 0x645
#endif
#ifndef CSR_HTINST
#define CSR_HTINST 0x64a
#endif
#ifndef CSR_HGATP
#define CSR_HGATP 0x680
#endif
#ifndef CSR_HGEIP
#define CSR_HGEIP 0xe12
#endif

#ifndef vsstatus
#define vsstatus CSR_VSSTATUS
#endif
#ifndef vsie
#define vsie CSR_VSIE
#endif
#ifndef vstvec
#define vstvec CSR_VSTVEC
#endif
#ifndef vsscratch
#define vsscratch CSR_VSSCRATCH
#endif
#ifndef vsepc
#define vsepc CSR_VSEPC
#endif
#ifndef vscause
#define vscause CSR_VSCAUSE
#endif
#ifndef vstval
#define vstval CSR_VSTVAL
#endif
#ifndef vsip
#define vsip CSR_VSIP
#endif
#ifndef vstimecmp
#define vstimecmp CSR_VSTIMECMP
#endif
#ifndef vstimecmph
#define vstimecmph CSR_VSTIMECMPH
#endif
#ifndef vsatp
#define vsatp CSR_VSATP
#endif
#ifndef mtinst
#define mtinst CSR_MTINST
#endif
#ifndef mtval2
#define mtval2 CSR_MTVAL2
#endif
#ifndef hstatus
#define hstatus CSR_HSTATUS
#endif
#ifndef hedeleg
#define hedeleg CSR_HEDELEG
#endif
#ifndef hideleg
#define hideleg CSR_HIDELEG
#endif
#ifndef hie
#define hie CSR_HIE
#endif
#ifndef htimedelta
#define htimedelta CSR_HTIMEDELTA
#endif
#ifndef hcounteren
#define hcounteren CSR_HCOUNTEREN
#endif
#ifndef hgeie
#define hgeie CSR_HGEIE
#endif
#ifndef henvcfg
#define henvcfg CSR_HENVCFG
#endif
#ifndef hedelegh
#define hedelegh CSR_HEDELEGH
#endif
#ifndef htimedeltah
#define htimedeltah CSR_HTIMEDELTAH
#endif
#ifndef henvcfgh
#define henvcfgh CSR_HENVCFGH
#endif
#ifndef htval
#define htval CSR_HTVAL
#endif
#ifndef hip
#define hip CSR_HIP
#endif
#ifndef hvip
#define hvip CSR_HVIP
#endif
#ifndef htinst
#define htinst CSR_HTINST
#endif
#ifndef hgatp
#define hgatp CSR_HGATP
#endif
#ifndef hgeip
#define hgeip CSR_HGEIP
#endif

// VRET encoding (HRET slot) for assemblers that lack a vret mnemonic.
#ifndef RVTEST_VRET_DEFINED
#define RVTEST_VRET_DEFINED
.macro VRET
  .insn i 0x73, 0, x0, x0, 0x202
.endm
#endif

// Page Table Macros

/* Set up the Page table entry for Sv32 Translation scheme
    Arguments:
    _PAR: Register containing Physical Address
    _PR: Register containing Permissions for Leaf PTE.
        (Note: No-leaf PTE (if-any) has only valid permission (pte.v) set)
    _TR0, _TR1, _TR2: Temporary registers used and modified by function
    VA: Virtual address
    level: Level at which PTE would be setup
        0: Two level translation
        1: Superpage
*/

#define LEVEL0 0x00
#define LEVEL1 0x01
#define LEVEL2 0x02
#define LEVEL3 0x03
#define LEVEL4 0x04

#define sv39 0x00
#define sv48 0x01
#define sv57 0x02

#define CODE code_bgn_off
#define DATA data_bgn_off
#define SIG  sig_bgn_off
#define VMEM vmem_bgn_off


#define SATP_SETUP(_TR0, _TR1, MODE);\
    LA(_TR0, rvtest_Sroot_pg_tbl) ;\
    LI(_TR1, MODE) ;\
    srli _TR0, _TR0, 12 ;\
    or _TR0, _TR0, _TR1  ;\
    csrw satp, _TR0   ;\

//****NOTE: label `rvtest_Sroot_pg_tbl` must be declared after RVTEST_DATA_END
//          in the test aligned at 4kiB (use .align 12)
#define PTE_SETUP_COMMON(_PAR, _PR, _TR0, _TR1, _VAR, level)      ;\
    srli _VAR, _VAR, (RISCV_PGLEVEL_BITS * level + RISCV_PGSHIFT) ;\
    srli _PAR, _PAR, (RISCV_PGLEVEL_BITS * level + RISCV_PGSHIFT) ;\
    slli _PAR, _PAR, (RISCV_PGLEVEL_BITS * level + RISCV_PGSHIFT) ;\
    LI(_TR0, ((1 << RISCV_PGLEVEL_BITS) - 1))                     ;\
    and _VAR, _VAR, _TR0                                          ;\
    slli _VAR, _VAR, ((XLEN >> 5)+1)                              ;\
    add _TR1, _TR1, _VAR                                          ;\
    srli _PAR, _PAR, 12                                           ;\
    slli _PAR, _PAR, 10                                           ;\
    or _PAR, _PAR, _PR                                            ;\
    SREG _PAR, 0(_TR1);

#define PTE_SETUP_RV32(_PAR, _PR, _TR0, _TR1, VA, level)    ;\
    srli _PAR, _PAR, 12                                         ;\
    slli _PAR, _PAR, 10                                         ;\
    or _PAR, _PAR, _PR                                          ;\
    .if (level==1)                                              ;\
        LA(_TR1, rvtest_Sroot_pg_tbl)                           ;\
        LI(_TR0, ((VA>>22)&0x3FF)<<2)                           ;\
    .endif                                                      ;\
    .if (level==0)                                              ;\
        LA(_TR1, rvtest_slvl1_pg_tbl)                           ;\
        LI(_TR0, ((VA>>12)&0x3FF)<<2)                           ;\
    .endif                                                      ;\
    add _TR1, _TR1, _TR0                                        ;\
    SREG _PAR, 0(_TR1);

// More Robust version of PTE_SETUP_32 to setup a PTE for a PA using Va
// in a single line.
//args: PA: Label of Physical Address, PERMS: permissions in hex
//args: VA: Virtual Address in hex, level: Level to store at
#define PTE_SETUP_RV32_New(PA_LBL, PERMS, VA, level)           ;\
    LA(a0, PA_LBL)                                             ;\
    LI(a1, PERMS)                                              ;\
  PTE_SETUP_RV32(a0, a1, t0, t1, VA, level)                  ;\

#define SAVE_AREA_SETUP(VA, PA_LBL, _REG_NAME)                  ;\
  LI (t0, VA)                                                 ;\
  LA (t1, PA_LBL)                                             ;\
  sub t0, t0, t1                                              ;\
  LREG t1, _REG_NAME##_bgn_off+0*sv_area_sz(sp)               ;\
  add t2, t1, t0                                              ;\
  SREG t2, _REG_NAME##_bgn_off+1*sv_area_sz(sp)               ;\

#define PTE_SETUP_RV64(_PAR, _PR, _TR0, _TR1, VA, level, mode)  ;\
    srli _PAR, _PAR, 12                                         ;\
    slli _PAR, _PAR, 10                                         ;\
    or _PAR, _PAR, _PR                                          ;\
    .if (mode == sv39)                                          ;\
        .if (level == 2)                                        ;\
            LA(_TR1, rvtest_Sroot_pg_tbl)                       ;\
            .set vpn, ((VA >> 30) & 0x1FF) << 3                 ;\
        .endif                                                  ;\
        .if (level == 1)                                        ;\
            LA(_TR1, rvtest_slvl1_pg_tbl)                       ;\
            .set vpn, ((VA >> 21) & 0x1FF) << 3                 ;\
        .endif                                                  ;\
        .if (level == 0)                                        ;\
            LA(_TR1, rvtest_slvl2_pg_tbl)                       ;\
            .set vpn, ((VA >> 12) & 0x1FF) << 3                 ;\
        .endif                                                  ;\
    .endif                                                      ;\
    .if (mode == sv48)                                          ;\
        .if (level == 3)                                        ;\
            LA(_TR1, rvtest_Sroot_pg_tbl)                       ;\
            .set vpn, ((VA >> 39) & 0x1FF) << 3                 ;\
        .endif                                                  ;\
        .if (level == 2)                                        ;\
            LA(_TR1, rvtest_slvl1_pg_tbl)                       ;\
            .set vpn, ((VA >> 30) & 0x1FF) << 3                 ;\
        .endif                                                  ;\
        .if (level == 1)                                        ;\
            LA(_TR1, rvtest_slvl2_pg_tbl)                       ;\
            .set vpn, ((VA >> 21) & 0x1FF) << 3                 ;\
        .endif                                                  ;\
        .if (level == 0)                                        ;\
            LA(_TR1, rvtest_slvl3_pg_tbl)                       ;\
            .set vpn, ((VA >> 12) & 0x1FF) << 3                 ;\
        .endif                                                  ;\
    .endif                                                      ;\
    .if (mode == sv57)                                          ;\
        .if (level == 4)                                        ;\
            LA(_TR1, rvtest_Sroot_pg_tbl)                       ;\
            .set vpn, ((VA >> 48) & 0x1FF) << 3                 ;\
        .endif                                                  ;\
        .if (level == 3)                                        ;\
            LA(_TR1, rvtest_slvl1_pg_tbl)                       ;\
            .set vpn, ((VA >> 39) & 0x1FF) << 3                 ;\
        .endif                                                  ;\
        .if (level == 2)                                        ;\
            LA(_TR1, rvtest_slvl2_pg_tbl)                       ;\
            .set vpn, ((VA >> 30) & 0x1FF) << 3                 ;\
        .endif                                                  ;\
        .if (level == 1)                                        ;\
            LA(_TR1, rvtest_slvl3_pg_tbl)                       ;\
            .set vpn, ((VA >> 21) & 0x1FF) << 3                 ;\
        .endif                                                  ;\
        .if (level == 0)                                        ;\
            LA(_TR1, rvtest_slvl3_pg_tbl)                       ;\
            .set vpn, ((VA >> 12) & 0x1FF) << 3                 ;\
        .endif                                                  ;\
    .endif                                                      ;\
    LI(_TR0, vpn)                                               ;\
    add _TR1, _TR1, _TR0                                        ;\
    SREG _PAR, 0(_TR1)                                          ;

#define PTE_PERMUPD_RV32(_PR, _TR0, _TR1, VA, level)            ;\
    .if (level==1)                                              ;\
        LA(_TR1, rvtest_Sroot_pg_tbl)                           ;\
        .set vpn, ((VA>>22)&0x3FF)<<2                           ;\
    .endif                                                      ;\
    .if (level==0)                                              ;\
        LA(_TR1, rvtest_slvl1_pg_tbl)                           ;\
        .set vpn, ((VA>>12)&0x3FF)<<2                           ;\
    .endif                                                      ;\
    LI(_TR0, vpn)                                               ;\
    add _TR1, _TR1, _TR0                                        ;\
    LREG _TR0, 0(_TR1)                                          ;\
    srli _TR0, _TR0, 10                                         ;\
    slli _TR0, _TR0, 10                                         ;\
    or _TR0, _TR0, _PR                                          ;\
    SREG _TR0, 0(_TR1)                                          ;


#define SATP_SETUP_SV32 ;\
    LA(t6, rvtest_Sroot_pg_tbl) ;\
    LI(t5, SATP32_MODE) ;\
    srli t6, t6, 12 ;\
    or t6, t6, t5  ;\
    csrw satp, t6   ;

#define SATP_SETUP_RV64(MODE)                                   ;\
    LA(t6, rvtest_Sroot_pg_tbl)                                 ;\
    .if (MODE == sv39)                                          ;\
    LI(t5, (SATP64_MODE) & (SATP_MODE_SV39 << 60))              ;\
    .endif                                                      ;\
    .if (MODE == sv48)                                          ;\
    LI(t5, (SATP64_MODE) & (SATP_MODE_SV48 << 60))              ;\
    .endif                                                      ;\
    .if (MODE == sv57)                                          ;\
    LI(t5, (SATP64_MODE) & (SATP_MODE_SV57 << 60))              ;\
    .endif                                                      ;\
    .if (MODE == sv64)                                          ;\
    LI(t5, (SATP64_MODE) & (SATP_MODE_SV64 << 60))              ;\
    .endif                                                      ;\
    srli t6, t6, 12                                             ;\
    or t6, t6, t5                                               ;\
    csrw satp, t6                                               ;
