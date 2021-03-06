#!/usr/bin/env python3

import pysam
import sys

docstring= """ 
FilterMutectCalls from GATK 4.0.1.0 or earlier has a bug with the MFRL tag.
It expects an INT, which is usually the case, but it fails if MFRL is float.
See https://github.com/broadinstitute/gatk/issues/4363

This script converts MFRL floats to INT so that the output can be passed to
FilterMutectCalls.  

Output goes to stdout in uncompressed format.

USAGE
fixMFRLforMutect <in.vcf> 

VERSION 0.2.0
"""

if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help']:
    print(docstring)
    sys.exit()

if len(sys.argv) == 1:
    vcf= pysam.VariantFile('-')
else:
    vcf= pysam.VariantFile(sys.argv[1])

try:
    header= str(vcf.header).strip()
    assert '##FORMAT=<ID=MFRL,Number=R,Type=Float' in header
    header= header.replace('##FORMAT=<ID=MFRL,Number=R,Type=Float', '##FORMAT=<ID=MFRL,Number=R,Type=Integer')
    print(str(header))

    for line in vcf:
        xline= str(line).strip().split('\t')
        mfrl_idx= xline[8].split(':').index('MFRL')
        for i in range(9, len(xline)):
            sample= xline[i].split(':')
            mfrl= sample[mfrl_idx].split(',')
            mfrl= [str(int(float(x))) for x in mfrl]
            mfrl= ','.join(mfrl)
            sample[mfrl_idx]= mfrl
            sample= ':'.join(sample)
            xline[i]= sample
        print('\t'.join(xline))
except (BrokenPipeError, IOError):
    pass

vcf.close()
sys.exit()
