#!/usr/bin/perl -w
# 
# Copyright (c)   AB_Life 2011
# Writer:         xuxiong <xuxiong19880610@163.com>
# Program Date:   2011.06.28
# Modifier:       xuxiong <xuxiong19880610@163.com>
# Last Modified:  2011.06.28
my $ver="1.0.0";

use strict;
use Getopt::Long;
use Data::Dumper;
use FindBin qw($Bin $Script);
use File::Basename qw(basename dirname);
use List::Util qw(first max maxstr min minstr reduce shuffle sum);

#Before writing your programmeyou must write the detailed timediscriptionsparameter and it's explanation,Meanwhile,annotation your programme in English if possible.

my %opts;
GetOptions(\%opts,"gff=s","peak=s","o=s" );

if(!defined($opts{gff}) || !defined($opts{peak}) || !defined($opts{o})  )
{
	print <<"	Usage End.";

	Description:This programme is used for filtering out the clusters within genes
		
		Version: $ver

	Usage:perl $0

		-gff           infile          must be given

		-peak          infile          must be given

		-o             outfile         must be given

	Usage End.

	exit;
}

###############Time_start##########
my $Time_Start;
$Time_Start = sub_format_datetime(localtime(time()));
print "\nStart Time :[$Time_Start]\n\n";
###################################

my $gff=$opts{gff};	
my $peak=$opts{peak};
my $out=$opts{o};

my %gene=();
my $n=0;
open (GFF,"<$gff") || die "Can't open $gff\n";			#open a file as reading
while (<GFF>) {
	chomp;
	next if(/^\#/);
	my @line=split(/\t/,$_);
#	if ($line[2]=~/^mRNA$/ && $line[-1]=~/^ID=(\S+\.1);Parent=\S+/ ){
	if ($line[2]=~/^gene|pseudogene|transposable_element_gene$/ && $line[-1]=~/^ID=([\w\.\-\:]+)/){
		my $geneid = $1;
		my $genename = $1;
		push @{$gene{$line[0]}},[($line[3],$line[4],$line[6],$geneid,$genename)];
		$n++;
	}
}
close(GFF);

# &sort_gene(\%gene);

print "gene_num: ",$n,"\n";
$n=0;

my %peaks = ();
my %peaknum = ();
$/=">";
open (PEAK,"<$peak") || die "Can't open $peak\n";			#open a file as reading
while (<PEAK>){
	chomp;
	next if (/^$/) ;
	next if (/^#/) ;
	my @unit=split(/\n/,$_);
	my @title=split("\t",shift(@unit));
	my $chr = $title[1];
	$peaknum{$chr} = 0 if not defined($peaknum{$chr}) ;
	my $strand = $title[7];
	my $start = $title[2];
	my $end = $title[3];
	my $id = $title[0];
	my $all = ">".$_;

	$peaks{$chr}->[$peaknum{$chr}]->{"start"} = $start;
	$peaks{$chr}->[$peaknum{$chr}]->{"end"} = $end;
	$peaks{$chr}->[$peaknum{$chr}]->{"strand"} = $strand;
	$peaks{$chr}->[$peaknum{$chr}]->{"id"} = $id;
	$peaks{$chr}->[$peaknum{$chr}]->{"all"} = $all;
	$peaknum{$chr}++ ;
	$n++;
}
close PEAK;
$/="\n";
print "peak_num: ",$n,"\n";
$n=0;

&sort_peak(\%peaks);

print `date`;
open (OUT,">$out") || die "Can't creat $out\n";		#open a file as writing
print OUT "#Gene:\tgenestart\tgeneend\tgenename\tgenestrand\n";
print OUT "##peak info\n";
print OUT "###current_sum_tag_len\tcurrent_len_gene\tcurrent_peak_num\tcurrent_tag_num\taverage_nucleotide_distribution\n";
foreach my $chr (sort keys %gene){
	my %usedpeaks = ();
	foreach my $thisgene (sort @{$gene{$chr}}){
		my $genestart = $thisgene->[0];
		my $geneend = $thisgene->[1];
		my $genestrand = $thisgene->[2];
		my $geneid = $thisgene->[3];
		my $genename = $thisgene->[4];
		my %peakflag = ();
		my @gene_peak=();
		# print "GENE:$genestart:$geneend:$genestrand\n";
		my ($current_sum_tag_len,$current_len_gene,$current_tag_num,$average_nucleotide_distribution,$current_peak_num)=(0,0,0,0,0);

		foreach my $thispeak (@{$peaks{$chr}}){
			my $this_peak_id = $thispeak->{"id"};
			next if defined($usedpeaks{$this_peak_id});
			my $this_peak_stand = $thispeak->{"strand"};
			if($genestrand ne $this_peak_stand){
				next;
			}
			my $this_peak_end = $thispeak->{"end"};
			next if $this_peak_end < $genestart;
			my $this_peak_start = $thispeak->{"start"};
			my $this_peak_all = $thispeak->{"all"};
			my $over_percent=&overlap_indentify($this_peak_start,$this_peak_end,$genestart,$geneend);
			if ($over_percent>=0.8) {
				push @gene_peak,$this_peak_all;
				$usedpeaks{$this_peak_id} = "";
				# print "yes\n";
			}
			last if $this_peak_start > $geneend;
		}

		if (@gene_peak) {
				&statistic_gene_peak_tag(\@gene_peak,\$current_sum_tag_len,\$current_tag_num,\$current_peak_num);
				$current_len_gene=abs($geneend-$genestart)+1;
				$average_nucleotide_distribution=sprintf("%3.4f",$current_sum_tag_len/$current_len_gene);
				if ($current_peak_num/$current_tag_num<1) {
					# print OUT "Gene:\t$chr\t$gene_start\t$gene_end\t$gene_strand\t$gene_name\n";
					print OUT "Gene:\t$genestart\t$geneend\t$genename\t$genestrand\n";
					for (my $i=0;$i<=$#gene_peak ;$i++) {
						print OUT $gene_peak[$i];
					}
					print OUT $current_sum_tag_len,"\t",$current_len_gene,"\t",$current_peak_num,"\t",$current_tag_num,"\t",$average_nucleotide_distribution,"\n";
				}
				
			}
		undef(@gene_peak);
		undef(%peakflag);
		print "done $genename\n";
	}
}

close OUT;

sub sort_gene{
	my $hash_ref=shift;
	foreach my $TEMP_CHRO (keys %{$hash_ref}) {
		@{$hash_ref->{$TEMP_CHRO}}= sort {$a->[0]<=>$b->[0] or $a->[1]<=>$b->[1]} @{$hash_ref->{$TEMP_CHRO}};
	}
}

sub sort_peak{
	my $hash_ref=shift;
	foreach my $TEMP_CHRO (keys %{$hash_ref}) {
		@{$hash_ref->{$TEMP_CHRO}}= sort {$a->{"start"}<=>$b->{"start"}} @{$hash_ref->{$TEMP_CHRO}};
	}
}



# my $gene_count=0;





# my $p_value;
# my @temp_current_gene=();
# my ($current_sum_tag_len,$current_len_gene,$current_tag_num,$average_nucleotide_distribution,$current_peak_num)=(0,0,0,0,0);
# open (OUT,">$out") || die "Can't creat $out\n";		#open a file as writing
# $/=">";
# open (PEAK,"<$peak") || die "Can't open $peak\n";			#open a file as reading
# while (<PEAK>){
# 	chomp;
# 	next if (/^$/) ;
# 	my @unit=split(/\n/,$_);
# 	my @title=split("\t",shift(@unit));
# 	if ($title[1] ne $initail_chr || $title[-1] ne $initail_strand) {
# 		if (@gene_peak) {
# 			$n++;
# 			&statistic_gene_peak_tag(\@gene_peak,\$current_sum_tag_len,\$current_tag_num,\$current_peak_num);
# 			$current_len_gene=abs($temp_current_gene[1]-$temp_current_gene[0])+1;
# 			$average_nucleotide_distribution=sprintf("%3.4f",$current_sum_tag_len/$current_len_gene);
# 			if ($current_peak_num/$current_tag_num<1) {
# 				print OUT "Gene:\t",join("\t",@temp_current_gene),"\n";
# 				for (my $i=0;$i<=$#gene_peak ;$i++) {
# 					print OUT $gene_peak[$i]->[0];
# 				}
# 				print OUT $current_sum_tag_len,"\t",$current_len_gene,"\t",$current_peak_num,"\t",$current_tag_num,"\t",$average_nucleotide_distribution,"\n";
# 			}
# 			#&cut_p_value(\@gene_peak,$average_nucleotide_distribution,0.01);
# 		}
# 		$initail_chr=$title[1];
# 		$initail_strand=$title[-1];
# 		$gene_count=0;
# 		($current_sum_tag_len,$current_len_gene,$current_tag_num,$average_nucleotide_distribution,$current_peak_num)=(0,0,0,0,0);
# 		if (exists $gene{$title[1]}{$title[-1]}) {
# 			@current_gene = @{$gene{$title[1]}{$title[-1]}[$gene_count]};
# 			push @current_gene,$title[-1];
# 		}
# 		@gene_peak=();
# 		$gene_id=$current_gene[3];
# 	}
# 	if ($title[2]>$current_gene[1]) {
# 		$gene_count++;
# 		@current_gene=@{$gene{$title[1]}{$title[-1]}[$gene_count]} if (defined @{$gene{$title[1]}{$title[-1]}[$gene_count]});
# 		push @current_gene,$title[-1];
# 		while ($title[2]>$current_gene[1]) {
# 			$gene_count++;
# 			if (not defined $gene{$title[1]}{$title[-1]}[$gene_count]) {
# 				last;
# 			}
# 			@current_gene=@{$gene{$title[1]}{$title[-1]}[$gene_count]};
# 			push @current_gene,$title[-1];
# 		}
# 	}
# 	if ($current_gene[3] ne $gene_id) {
# 		if (@gene_peak) {
# 			$n++;
# 			&statistic_gene_peak_tag(\@gene_peak,\$current_sum_tag_len,\$current_tag_num,\$current_peak_num);
# 			$current_len_gene=abs($temp_current_gene[1]-$temp_current_gene[0])+1;
# 			$average_nucleotide_distribution=sprintf("%3.4f",$current_sum_tag_len/$current_len_gene);
# 			if ($current_peak_num/$current_tag_num<1) {
# 				print OUT "Gene:\t",join("\t",@temp_current_gene),"\n";
# 				for (my $i=0;$i<=$#gene_peak ;$i++) {
# 					print OUT $gene_peak[$i]->[0];
# 				}
# 				print OUT $current_sum_tag_len,"\t",$current_len_gene,"\t",$current_peak_num,"\t",$current_tag_num,"\t",$average_nucleotide_distribution,"\n";
# 			}
# #			&cut_p_value(\@gene_peak,$average_nucleotide_distribution,0.01);
# 		}
# 		@gene_peak=();
# 		($current_sum_tag_len,$current_len_gene,$current_tag_num,$average_nucleotide_distribution,$current_peak_num)=(0,0,0,0,0);
# 		$gene_id=$current_gene[3];
# 	}
# 	my $over_percent=&overlap_indentify($title[2],$title[3],$current_gene[0],$current_gene[1]);
# 	if ($over_percent>=0.8) {
# 		my @cluster_line=();
# 		@temp_current_gene=@current_gene[0,1,2,4];
# #		push @cluster_line,join("\t",@current_gene);
# 		push @cluster_line,">$_";
# #		my @cluster_pos=split(";",$line[-1]);
# #		my $max_cluster_height=&max_cluster_height(\@cluster_pos);
# #		unshift @cluster_line,$max_cluster_height;
# 		push @gene_peak,[@cluster_line];
# #		print OUT join("\n",@cluster_line),"\n";
# 	}
# 	if (eof(PEAK)) {
# 		if (@gene_peak) {
# 			$n++;
# 			&statistic_gene_peak_tag(\@gene_peak,\$current_sum_tag_len,\$current_tag_num,\$current_peak_num);
# 			$current_len_gene=abs($temp_current_gene[1]-$temp_current_gene[0])+1;
# 			$average_nucleotide_distribution=sprintf("%3.4f",$current_sum_tag_len/$current_len_gene);
# 			if ($current_peak_num/$current_tag_num<1) {
# 				print OUT "Gene:\t",join("\t",@temp_current_gene),"\n";
# 				for (my $i=0;$i<=$#gene_peak ;$i++) {
# 					print OUT $gene_peak[$i]->[0];
# 				}
# 				print OUT $current_sum_tag_len,"\t",$current_len_gene,"\t",$current_peak_num,"\t",$current_tag_num,"\t",$average_nucleotide_distribution,"\n";
# 			}
# 			#&cut_p_value(\@gene_peak,$average_nucleotide_distribution,0.01);
# 		}
# 	}
# }
# close(OUT);
# close(PEAK);


# print "gene_peak: ",$n,"\n";
# sub cut_p_value{
# 	my ($array,$aver_nuc_dis,$cutoff_p_value)=@_;
# 	for (my $i=0;$i<=$#{$array} ;$i++) {
# 		my $p_value=$aver_nuc_dis/$array->[$i]->[0];
# 		if ($p_value<$cutoff_p_value) {
# 			$p_value=sprintf("%2.4f",$p_value);
# 			print $p_value,"\t",join("\t",@{$array->[$i]}),"\n";
# 		}
# #		else{
# #			print join("\t",@{$array->[$i]}),"\n";
# #		}
# 	}
# }

# sub statistic_gene_peak_tag{
# 	my ($array,$tag_num,$peak_num)=@_;
# 	$$peak_num=scalar(@{$array});
# 	for (my $i=0;$i<=$#{$array} ;$i++) {
# 		my @tag_line=split(/\t/,$array->[$i]);
# 		$$tag_num+=$tag_line[4];
# 	}
# }

sub statistic_gene_peak_tag{
	my ($array,$sum_tag_len,$tag_num,$peak_num)=@_;
	$$peak_num=scalar(@{$array});
	for (my $i=0;$i<=$#{$array} ;$i++) {
		my @tag=split("\n",$array->[$i]);
		for (my $j=0;$j<=$#tag;$j++) {
			my @tag_line=split(/\t/,$tag[$j]);
			if ($j==0) {
				$$tag_num+=$tag_line[4];
			}
			else{
				my $temp_tag_len=abs($tag_line[2]-$tag_line[1])+1;
				$$sum_tag_len+=$temp_tag_len;
			}
		}
	}
#	print $$sum_tag_len,"\t",$$tag_num,"\n";
}



sub overlap_indentify{
	my ($start1,$end1,$start2,$end2)=@_;
	my $overlap_percent=0;
	if($end1<$start2||$start1>$end2){
		$overlap_percent=0;
		return $overlap_percent;
	}elsif($start1>=$start2&&$end1<=$end2){
		$overlap_percent=1;
		return $overlap_percent;
	}elsif($start1<=$start2&&$end1>=$start2){
		$overlap_percent=sprintf("%2.3f",($end1-$start2)/($end1-$start1));
		return $overlap_percent;
	}elsif($end1>=$end2&&$start1<=$end2){
		$overlap_percent=sprintf("%2.3f",($end2-$start1)/($end1-$start1));
		return $overlap_percent;
	}elsif($start1<=$start2&&$end1>=$end2){
		$overlap_percent=sprintf("%2.3f",($end2-$start2)/($end1-$start1));
		return $overlap_percent;
	}
}

# sub max_cluster_height{
# 	my ($array) =@_;
# 	my %hash=();
# 	my $max_height;
# 	my $max_count;
# 	for (my $i=0;$i<=$#{$array} ;$i++) {
# 		my @tmp_pos=split(",",$array->[$i]);
# 		for (my $j=$tmp_pos[0];$j<=$tmp_pos[1] ;$j++) {
# 			$hash{$j}++;
# 		}
# 	}
# 	my @values=values %hash;
# 	&max(\@values,\$max_height,\$max_count);
# 	return $max_height;
# }

# sub max {
# 	my ($array,$max,$max_count)=@_;
# 	$$max=$array->[0];
# 	$$max_count=0;
# 	for (my $i=1;$i<= $#{$array} ;$i++) {
# 		if ($array->[$i]>$$max){
# 			$$max = $array->[$i] ;
# 			$$max_count = $i;
# 		}
# 	}
# }

###############Time_end###########
my $Time_End;
$Time_End = sub_format_datetime(localtime(time()));
print "\nEnd Time :[$Time_End]\n\n";

###############Sub_format_datetime
sub sub_format_datetime {#Time calculation subroutine
    my($sec, $min, $hour, $day, $mon, $year, $wday, $yday, $isdst) = @_;
	$wday = $yday = $isdst = 0;
    sprintf("%4d-%02d-%02d %02d:%02d:%02d", $year+1900, $mon+1, $day, $hour, $min, $sec);
}
