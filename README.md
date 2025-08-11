### NGS sequence processing
biopanning NGS/ AI protein-folding method for selection of epitope-specific clones from an enriched pool
Consists of :
* Raw read QC filtering
* Reverse/ forward read stitching
* Generation of pairing combinations
* Structure/ binding pose prediction and selection
```
                                                                        _ _              _ _                                                                     
                                                                        \\\\            ////
----x--xx--                   -----------          ---------------       \\\\          ////
      -----------             ||||||                                      \\\\        ////
xxx---x-x--              -----------                                       \\\\      ////
-----------        --->                    --->    --------------- --->       \\    //
-----------             -----------                                            \\  //
      -----------          ||||||||                                             \\//
---x-xxx---                ------------                                         ||||
                                                                                ||||
                                                                                ||||                                                                                                                                     
  
```
NGS generated using MiSeq Illumina 
Each Vh and Vl have a forward and reverse read of 300 bp with a 100 bp overlap, making a read of 500 bp.

Quality filtering, read stitching (2x300-> 500) and clustering done either following [Faheed et. al.](https://doi.org/10.1007/978-1-0716-2609-2_25) for scripts see [dekoskylab - github](https://github.com/dekoskylab/CSHL_protocols/tree/main/Scripts/Scripts%20for%20Clonal%20Lineage%20and%20Gene%20Diversity%20Analysis%20of%20Paired%20Antibody%20Heavy%20and%20Light%20Chains)
OR 
IGX.Bio or similar platform 

Rank clusters according to sequence count
| Unique Cluster ID | Unique Sequence ID | Sequence Count | Receptor Amino Acids | Unique Cluster ID | Clone Count | Receptor Amino Acids |
|---:|---:|---:|:---|---:|---:|:---|
| 304 | 5514099422 | 422650 | QVQLVQSGAEVK... | 756 | 351086 | SYELTQPPSVSV... |
| 1385 | 5522630494 | 220739 | EVQLVESGGGVV... | 1197 | 153364 | QSVLTQPPSASG... |
| 589 | 5528116190 | 209780 | EVQLVQSGAEVK... | 2027 | 121194 | DIVMTQTPLSS... |
| 964 | 5506832094 | 77900 | QVQLVQSGGEVK... | 309 | 84728 | QSALTQPASVSG... |
| 1816 | 5522714718 | 56053 | QVQLVQSGAEVK... | 2442 | 67530 | LVLTQPPSASGT... |
| 2331 | 5539183454 | 48186 | QVQLVQSGAEVK... | 3520 | 32161 | SYELTQPPSVSV... |
| 70 | 5509774174 | 41788 | EVQLVESGGGVV... | 2743 | 27791 | QSVLTQPPSASG... |
| 1640 | 5533366750 | 39739 | EVQLVQSGAEVK... | 2141 | 26360 | DIVMTQTPLSSP... |
| 1056 | 5504278366 | 36747 | QVQLVQSGGEVK... | 410 | 25812 | QSALTQPASVSG... |


### Prepare and run boltz-2 prediction 

Enter the sequence in 
```NGS_clone_pair_gui.py```
to generate the .yaml input files for Boltz_2

Then run boltz-2 using
```boltz predict path/to/.yaml/files --recycling_steps 10 --diffusion_samples 50 --devices 4 --use_msa_server --out_dir /path/to/output_dir```
example batch submission script 

### Post boltz-2 data processing
see [boltz_2_out](https://github.com/jwohlwend/boltz/blob/main/docs/prediction.md#output) for output data structure.
Extract model metrics iPTM per chain iPTM, confidence score and distance of CDR loops from the epitope of interest using 
``Post_boltz_analysis.py``. Set IPTM and distance tolerance and select clones for validation, 
example output:
| name | confidence_score | IPTM | pci_AB | pci_AC | pci_BC | Heavy_chain_aa | Light_chain_aa | LCDR3_distance | HCDR3_distance |
|:---|:---|---:|---:|---:|---:|:---|:---|---:|---:|
| 4195_3384 | 0.932207584 | 0.883947492 | 0.827604175 | 0.796309948 | 0.953715801 | QVQLVQSGAEVK... | SYELTQPPSVSV... | 28.85266607 | 35.39199416 |
| 6780_1324 | 0.939061344 | 0.883887827 | 0.809440792 | 0.806204796 | 0.960929215 | EVQLVESGGGVV... | QSVLTQPPSASG... | 29.93869586 | 29.61526305 |
| 8054_5560 | 0.917029381 | 0.864742279 | 0.827312648 | 0.819780231 | 0.951842248 | EVQLVQSGAEVK... | DIVMTQTPLSSP... | 41.74955214 | 36.26729598 |
| 2635_60 | 0.911410153 | 0.864607811 | 0.76526314 | 0.800935864 | 0.965932608 | QVQLVQSGGEVK... | QSALTQPASVSG... | 41.59842986 | 38.77777021 |
| 4184_3320 | 0.92149657 | 0.862962604 | 0.780314147 | 0.759235084 | 0.964734972 | QVQLVQSGAEVK... | LVLTQPPSASGT... | 31.27739175 | 37.67254607 |

