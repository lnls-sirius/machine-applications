#!/usr/bin/env python-sirius
"""ID feedforward IOC executable."""

import sys

from si_ap_idff import si_ap_idff as ioc_module


def main():
    """Launch IOC."""
    idname = sys.argv[1]

    # select by idname what correctors belong to IDFF
    kwargs = dict(
        enbl_chcorrs=False, enbl_cvcorrs=False,
        enbl_qscorrs=False, enbl_lccorrs=False,
        enbl_qncorrs=False)
    if idname in ('SI-08SB:ID-IVU18', 'SI-14SB:ID-IVU18'):
        kwargs.update(
            dict(enbl_qncorrs=True))
    elif idname in ('SI-10SB:ID-DELTA52', 'SI-10SB:ID-EPU50'):
        kwargs.update(
            dict(enbl_chcorrs=True, enbl_cvcorrs=True, enbl_qscorrs=True))

    ioc_module.run(sys.argv[1], **kwargs)


if __name__ == "__main__":
    main()
