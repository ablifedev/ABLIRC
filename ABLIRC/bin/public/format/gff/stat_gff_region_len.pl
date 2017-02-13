#!/usr/bin/perl
use strict;
use warnings;
use FindBin qw($Bin $Script);
my @bin=split(/\//,$Bin);
my $len=scalar(@bin);
my $Bin=join('/',@bin[0..$len-4]);
use File::Basename qw(basename dirname);

my $gff=$ARGV[0];
my $chrlen_file = $ARGV[1];
my $outfile=$ARGV[2];
my $gene_model_file=$ARGV[3] if defined($ARGV[3]);


my $current_dir = `pwd`;chomp($current_dir);

if (! @ARGV) {
	print "perl $0 GFF_file chrlen_file out_file gene_model_file\n";
	exit;
}

my $total_len = 0;
open CHRLEN,"$chrlen_file";
while(<CHRLEN>){
	chomp;
	my @line=split;
	$total_len+=$line[1];
}

my %gene_model;
&load_gene_model($gene_model_file,\%gene_model) if (defined $gene_model_file) ;

my %gene=();
&load_gff($gff,\%gene,\%gene_model) if (defined $gene_model_file) ;
&load_gff_0($gff,\%gene) if (not defined $gene_model_file) ;
# &load_gff_0($gff,\%gene,\%gene_model) ;

my $intergenic_len = 0;
my $intron_len = 0;
my $noncoding_exon_len = 0;
my $cds_len=0;
my $three_prime_UTR_len=0;
my $five_prime_UTR_len=0;

$intergenic_len = $total_len-$gene{"rna"}{"total"};
print $gene{"exon"}{"exon"},"\n";
$gene{"exon"}{"exon"}=$gene{"exon"}{"coding"}+$gene{"exon"}{"exon"} if $gene{"exon"}{"exon"}<$gene{"exon"}{"coding"};
$intron_len = $gene{"rna"}{"total"}-$gene{"exon"}{"exon"};
$noncoding_exon_len = $gene{"exon"}{"exon"}-$gene{"exon"}{"coding"};
$cds_len=$gene{"exon"}{"CDS"};
$three_prime_UTR_len=$gene{"exon"}{"three_prime_UTR"};
$five_prime_UTR_len=$gene{"exon"}{"five_prime_UTR"};

my %gene_type=();

$gene_type{"intergenic"}=$intergenic_len if $intergenic_len>=0;
$gene_type{"intron"}=$intron_len if $intron_len>=0;
$gene_type{"noncoding_exon"}=$noncoding_exon_len if $noncoding_exon_len>=0;
$gene_type{"CDS"}=$cds_len if $cds_len>=0;
$gene_type{"three_prime_UTR"}=$three_prime_UTR_len if $three_prime_UTR_len>=0;
$gene_type{"five_prime_UTR"}=$five_prime_UTR_len if $five_prime_UTR_len>=0;


#foreach my $type (%gene_type) {
#	print $type.":".$gene_type{$type}."\n" if (exists $gene_type{$type}) ;
#}

&output($outfile,\%gene_type);

sub output{
	my ($o,$hash_ref)=@_;
	my $total_nu=0;
	open(OUT, ">Length_distribution_across_Genomic_Regions") or die $!;
	print OUT "+Region_Type\tLength\n";
	foreach my $keys (sort keys %{$hash_ref}) {
		print OUT $keys,"\t",sprintf("%10.2f",$hash_ref->{$keys}),"\n" if ($hash_ref->{$keys}) ;
		$total_nu+=$hash_ref->{$keys} if ($hash_ref->{$keys}) ;
	}
	close OUT;

	my $cmd = 'Rscript '.$Bin.'/plot/Bar_single_Mapping_distribution.r -f Length_distribution_across_Genomic_Regions -t Length_distribution_across_Genomic_Regions -n Length_distribution_across_Genomic_Regions -o ./ && rm -rf Length_distribution_across_Genomic_Regions ';
	system($cmd);
	open(OUT, ">Length_distribution_across_Genomic_Regions.xls") or die $!;
	print OUT "Region_Type\tPercent\n";
	foreach my $keys (sort keys %{$hash_ref}) {
		print OUT $keys,"\t",sprintf("%10.2f",$hash_ref->{$keys}),"(",sprintf("%.2f",100*$hash_ref->{$keys}/$total_nu),"\%)","\n" if ($hash_ref->{$keys}) ;
	}
	close OUT;
}

sub load_gene_model{
	my ($gene_model_infile,$gene_id_ref)=@_;
	open(IN,"<$gene_model_infile") || die $!;
	$/="\n";
	while (<IN>) { 
		chomp;
		my @line = split(/\t/);
		$gene_id_ref->{$line[-1]}=1;
	}
	close IN;
}

sub load_gff{
	my ($infile,$hash_ref,$gene_id_ref)=@_;
	my $transcript_count=0;
	my $gene_id="";
	my $transcript="";
	my $tag=0;
	my $start=0;
	my $end=0;
	my $len=0;
	open (IN ,"<$infile") || die "Can't open $!";
	$/="\n";
	while (<IN>) { ###open gff file
		chomp;
		next if ($_!~/^[\w\.]+/) ;
		my @line=split(/\t/,$_);
		if ($line[2]=~/^gene|pseudogene|transposable_element_gene$/){
			$start=$line[3];
			$end=$line[4];
			$len=$end-$start+1;
			$hash_ref->{"gene"}{"gene"} = 0 if not defined($hash_ref->{"gene"}{"gene"});
			$hash_ref->{"gene"}{"gene"}+=$len;
		}
		else{
			if ($line[2]=~/^mRNA|miRNA|mRNA_TE_gene|ncRNA|pseudogenic_transcript|rRNA|snoRNA|snRNA|tRNA|transcript$/){
				$line[-1]=~/^ID=([\w\.\-\%\:]+)/;
				if (defined($gene_id_ref->{$1})) {
					$tag=1;
					$transcript=$line[2];
					$start=$line[3];
					$end=$line[4];
					$len=$end-$start+1;
					$hash_ref->{"rna"}{$line[2]} = 0 if not defined($hash_ref->{"rna"}{$line[2]});
					$hash_ref->{"rna"}{$line[2]}+=$len;
					$hash_ref->{"rna"}{"total"} = 0 if not defined($hash_ref->{"rna"}{"total"});
					$hash_ref->{"rna"}{"total"}+=$len;
				}
				else{
					$tag=0;
				}
			}
			if ($tag==1) {
				if($line[2]=~/^three_prime_UTR|five_prime_UTR|CDS$/){
					next if ($transcript_count>1) ;
					$start=$line[3];
					$end=$line[4];
					$len=$end-$start+1;
					$hash_ref->{"exon"}{$line[2]} = 0 if not defined($hash_ref->{"exon"}{$line[2]});
					$hash_ref->{"exon"}{$line[2]}+=$len;
					$hash_ref->{"exon"}{"coding"} = 0 if not defined($hash_ref->{"exon"}{"coding"});
					$hash_ref->{"exon"}{"coding"}+=$len;
				}
				if($line[2]=~/^exon|pseudogenic_exon$/){
					next if ($transcript_count>1) ;
					$start=$line[3];
					$end=$line[4];
					$len=$end-$start+1;
					$hash_ref->{"exon"}{"exon"} = 0 if not defined($hash_ref->{"exon"}{"exon"});
					$hash_ref->{"exon"}{"exon"}+=$len;
				}
			}
			
		}
	}
	close IN;
}

sub load_gff_0{
	my ($infile,$hash_ref)=@_;
	my $transcript_count=0;
	my $gene_id="";
	my $transcript="";
	my $start=0;
	my $end=0;
	my $len=0;
	open (IN ,"<$infile") || die "Can't open $!";
	$/="\n";
	while (<IN>) { ###open gff file
		chomp;
		next if ($_!~/^[\w\.]+/) ;
		my @line=split(/\t/,$_);
		if ($line[2]=~/^gene|pseudogene|transposable_element_gene$/){
			$transcript="";
			$transcript_count=0;
			$start=$line[3];
			$end=$line[4];
			$len=$end-$start+1;
			$hash_ref->{"gene"}{"gene"} = 0 if not defined($hash_ref->{"gene"}{"gene"});
			$hash_ref->{"gene"}{"gene"}+=$len;
		}
		else{
			if ($line[2]=~/^mRNA|miRNA|mRNA_TE_gene|ncRNA|pseudogenic_transcript|rRNA|snoRNA|snRNA|tRNA|transcript$/){
				$transcript_count++;
				next if ($transcript_count>1) ;
				$transcript=$line[2];
				$start=$line[3];
				$end=$line[4];
				$len=$end-$start+1;
				$hash_ref->{"rna"}{$line[2]} = 0 if not defined($hash_ref->{"rna"}{$line[2]});
				$hash_ref->{"rna"}{$line[2]}+=$len;
				$hash_ref->{"rna"}{"total"} = 0 if not defined($hash_ref->{"rna"}{"total"});
				$hash_ref->{"rna"}{"total"}+=$len;
			}
			if($line[2]=~/^three_prime_UTR|five_prime_UTR|CDS$/){
				next if ($transcript_count>1) ;
				$start=$line[3];
				$end=$line[4];
				$len=$end-$start+1;
				$hash_ref->{"exon"}{$line[2]} = 0 if not defined($hash_ref->{"exon"}{$line[2]});
				$hash_ref->{"exon"}{$line[2]}+=$len;
				$hash_ref->{"exon"}{"coding"} = 0 if not defined($hash_ref->{"exon"}{"coding"});
				$hash_ref->{"exon"}{"coding"}+=$len;
			}
			if($line[2]=~/^exon|pseudogenic_exon$/){
				next if ($transcript_count>1) ;
				$start=$line[3];
				$end=$line[4];
				$len=$end-$start+1;
				$hash_ref->{"exon"}{"exon"} = 0 if not defined($hash_ref->{"exon"}{"exon"});
				$hash_ref->{"exon"}{"exon"}+=$len;
			}
		}
	}
	close IN;
}