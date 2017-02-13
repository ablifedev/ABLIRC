#! /usr/bin/env perl

use strict;

use warnings;

use Getopt::Long;

use Data::Dumper;

use HTML::Table;

my $indir = "./";
my @raw=();
my $raw_postfix="fastqc";


##### Main_Program_End ################
&load_raw_data($indir,\@raw,$raw_postfix);
left_frame();
right_frame();
main_frame();


#==============Subroutines===============#
# main frame
sub main_frame{
	open MAINFRAME, '>', "fastqc.html";
	
	print MAINFRAME <<EOF;
	<html>
 	<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
	<head>

		<title>fastqc  </title>
		<meta name="keywords" content="deep sequecing, HiSeq, mireap">
		<meta name="description" content="Result display">

		<style> 
		"f:*{behavior:url(#default#vml)}" 
		</style> 
	</head>

 <body>
		<table width="100%" border="0">
			<tbody>
				<tr>
					<td height="900px" width="20%">
						<iframe src="left_frame.html" name="left_frame" width="100%" height="100%">
						</iframe>
					</td>
					<td height="900px" width="80%">
						<iframe name="right_frame" src="right_frame.html" width="100%" height="100%" scrolling="auto">						
						</iframe>
					</td>
				</tr>
			</tbody>
		</table>
	</body>
 </html>
EOF
close MAINFRAME;
}

# print left frame
sub left_frame{
	
	open LEFT, '>', "left_frame.html";
	
	print LEFT <<EOF;
	
	<html>
	<head>
		<title>fastqc  </title>
		<meta name="keywords" content="sequecing, miRNA, genome">
		<meta name="description" content="Result display">
		<meta http-equiv="Content-Type" content="text/html; charset=UTF8">
		<style> 
		"f:*{behavior:url(#default#vml)} "
			</style> 
	</head>

	<body style="font-family:Arial">
		<xml:namespace prefix="f">
			<ol>
			<font size=3>
EOF

foreach my $fastqc (@raw){
	my $name = $fastqc;
	$name =~s/\.fq\.clean_fq_fastqc//;
	my $tmp = "<li><a target=\"right_frame\" href=\"$fastqc/fastqc_report.html\">$name</a></li>";
	print LEFT $tmp,"\n";
}
		print LEFT <<EOF;
			</font>
			</ol>

	</ol>
	</ul>
	</xml:namespace>
	</body>
</html>
EOF

close LEFT;

}

# produce right frame
# all the samples on the same page
sub right_frame{
	
	open RIGHT, '>', "right_frame.html";
	
	print RIGHT <<EOF;
	<html>
 	<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
	<head>
		<title>FastQC Report</title>
	</head>
	<body style="font-family:Arial" bgcolor="beige">
			<p>
			</P>
			<h3><font size=5>FastQC Report</font></h3>

EOF
	
	print RIGHT <<EOF;
	</body>
 </html>
EOF

close RIGHT;

}


sub load_raw_data{
	my ($INDIR,$filenames_ref,$RAW_POSTFIX)=@_;
	opendir(DIR,$INDIR) or die "Can't open $INDIR: $!";
	my $tmp;
	while ($tmp=readdir(DIR)) {
		chomp $tmp;
		next if ($tmp!~/$RAW_POSTFIX$/) ;
		push @{$filenames_ref},$tmp;
	}
	@{$filenames_ref} = sort @{$filenames_ref};
	close(DIR);
}
