#! /usr/bin/env perl



use strict;
use warnings;
use Data::Dumper;

my ($cluster_info, $times) = @ARGV;

# chr20   31720350        31720374        chr20_263509    1       -       intron:1.0;     ENSG00000171552.12
# chr20   12894363        12894393        chr20_262563    2       -       noncoding_exon:1.0;     ENSG00000233048.1
# chr20   48930738        48930847        chr20_259952    9       +       intron:1.0;     ENSG00000124198.8
# chr20   34371601        34371627        chr20_258224    1       +       intron:1.0;     ENSG00000078747.12

my %gene = ();
open IN,"$cluster_info";
while(<IN>){
    chomp;
    my @line=split(/\t/);
    my $len = $line[2]-$line[1]+1;
    $gene{$line[-1]} = 0 if not defined($gene{$line[-1]});
    $gene{$line[-1]} += $len;
}
close IN;

open OUT,">trans_length.txt";
foreach my $g (keys %gene){
    print OUT "$g\t",$gene{$g}*$times,"\n";
}
close OUT;