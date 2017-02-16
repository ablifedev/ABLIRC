#!/usr/bin/perl
# @Author: anchen
# @Date:   2016-08-17 15:53:19
# @Last Modified by:   anchen
# @Last Modified time: 2016-11-21 14:29:26
#!/usr/bin/perl -w
use strict;
use Getopt::Long;

=head1 Description

Program: clip_peak_overlap_info

Author: Ablife

Version: 1.0

使用bedtools cluster将ablife,piranha,cims三种方法得到的peak进行cluster后，需对应回源文件，补充完整的peak信息，同时加入cluster信息

=head1 Usage

perl nonoverlap_CIMS.pl [options]

    -a   ablife addanno peak file, required

    -b   piranha addanno peak file, required

    -c   cims addanno peak file, required

    -i   cluster info, required

    -o   result file, default is "allpeaks_cluster_type.bed"

    -h      output help information

=cut

die `pod2text $0` if (@ARGV < 4);

my ($sample1,$sample2,$info,$out,$help);
GetOptions(
            "a:s"=>\$sample1,
            "b:s"=>\$sample2,
            "i:s"=>\$info,
            "o:s"=>\$out,
            "h"=>\$help
            );

die `pod2text $0` if ($help);

$out||="allpeaks_cluster_type.bed";

print "Command:\n  perl $0 -a $sample1 -b $sample2 -i $info -o $out\n\n";

my (@line,%hash1,%hash2,%hash3,$key,$value);

open A,"$sample1";
while (<A>){
    chomp;
    next if(/^#/);
    @line=split /\t/,$_;
    my $key = join("\t",@line[0..5]);
    $hash1{$key}=$_;
}
close A;
open A,"$sample2";
while (<A>){
    chomp;
    next if(/^#/);
    @line=split /\t/,$_;
    my $key = join("\t",@line[0..5]);
    $hash2{$key}=$_;
}
close A;

open INFO,"$info";
while (<INFO>){
    chomp;
    @line=split /\t/,$_;
    my $key = join("\t",@line[0..5]);
    $hash3{$key}=@line[-1];
}
close INFO;
open OUT, ">$out";
print OUT "AAA";
while(($key,$value)=each(%hash3)){
    if (exists $hash1{$key}){
        print OUT $hash1{$key},"\t",$value,"\tsample1\n";
    }
    elsif (exists $hash2{$key}){
        print OUT $hash2{$key},"\t",$value,"\tsample2\n";
    }
}   

close OUT;

#################################
########## Sub Routine ##########
#################################
