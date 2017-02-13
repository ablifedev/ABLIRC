#!/usr/bin/perl
use strict;
use warnings;
use FindBin qw($Bin $Script);
use File::Basename qw(basename dirname);

my $gff=$ARGV[0];
my $outfile=$ARGV[1];

my $current_dir = `pwd`;chomp($current_dir);

if (! @ARGV) {
	print "perl $0 GFF_file out_file\n";
	exit;
}
my %gene=();
&load_gff($gff,\%gene);

my %gene_type=();

foreach my $chr (sort keys %gene) {
	foreach my $id (keys %{$gene{$chr}}) {
		$gene_type{$gene{$chr}{$id}->[1]->[0]->[1]}++ if defined($gene{$chr}{$id}->[1]->[0]->[1]);
	}
}


#foreach my $type (%gene_type) {
#	print $type.":".$gene_type{$type}."\n" if (exists $gene_type{$type}) ;
#}

&output($outfile,\%gene_type);

sub output{
	my ($o,$hash_ref)=@_;
	open(OUT, ">$o.gene_type") or die $!;
	foreach my $keys (sort keys %{$hash_ref}) {
		print OUT $keys,"\t",sprintf("%10.2f",$hash_ref->{$keys}),"\n" if ($hash_ref->{$keys}) ;
	}
	close OUT;
	`cat $Bin/Pie_Chart.r|R --slave --args $current_dir $o.gene_type `;
}

sub load_gff{
	my ($infile,$hash_ref)=@_;
	my $transcript_count=0;
	my $gene_id="";
	my $transcript="";
	open (IN ,"<$infile") || die "Can't open $!";
	$/="\n";
	while (<IN>) { ###open gff file
		chomp;
		next if ($_!~/^[\w\.]+/) ;
		my @line=split(/\s+/,$_);
		if ($line[2]=~/^gene|pseudogene|transposable_element_gene$/ && $line[-1]=~/^ID=\S+;Name=([\w\_\.\%]+)/){
			$gene_id = $1 ; 
			$transcript="";
			$transcript_count=0;
			push @{$hash_ref->{$line[0]}{$gene_id}->[$transcript_count]},($line[6],$line[2],$line[3],$line[4]);
		}
		else{
			if ($line[2]=~/^mRNA|miRNA|mRNA_TE_gene|ncRNA|pseudogenic_transcript|rRNA|snoRNA|snRNA|tRNA|transcript$/){
				$transcript=$line[2];
				$transcript_count++;
				push @{$hash_ref->{$line[0]}{$gene_id}->[$transcript_count]},[($line[6],$line[2],$line[3],$line[4])];
			}
			if ($transcript=~/^mRNA$|^$/) {
				if($line[2]=~/^three_prime_UTR|five_prime_UTR|CDS$/){
					push @{$hash_ref->{$line[0]}{$gene_id}->[$transcript_count]},[($line[6],$line[2],$line[3],$line[4])];
				}
			}
			else{
				if($line[2]=~/^exon|pseudogenic_exon$/){
					push @{$hash_ref->{$line[0]}{$gene_id}->[$transcript_count]},[($line[6],$line[2],$line[3],$line[4])];
				}
			}
		}
	}
	close IN;
}
