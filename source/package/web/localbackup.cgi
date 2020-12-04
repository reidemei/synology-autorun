#!/usr/bin/perl -w

use CGI qw/:standard/;
use CGI::Carp qw(fatalsToBrowser);
use File::Temp qw/ tempfile tempdir /;

print "Content-type: text/html\n\n";

# check authentication
if (open (IN,"/usr/syno/synoman/webman/modules/authenticate.cgi|")) {
    $user=<IN>;
    chop($user);
    close(IN);
}
if ($user ne "admin") {
    print "<HTML><HEAD><TITLE>Login Required</TITLE></HEAD><BODY>Please login as admin first, before using this webpage<br/><br/>";
    die;
}

# read the config
if (open (IN, "/var/packages/autorun/target/config")) {
    while (<IN>) {
	chomp;
	s/#.//;
	s/^\s+//;
	s/\s+$//;
	my ($var, $value) = split(/\s*=\s*/, $_, 2);
	$tmplhtml{$var}=$value;
    }
    close (IN);
}

# is there an action?
$action = param ('action');
if ($action eq "create") {
    # get the parameter
    $file = param ('file');
    $target = param ('target');
    $backup = param ('backup');
    $eject = param ('eject');
    $encrypt = param ('encrypt');
    $encryptfilename = param ('encryptfilename');
    $password = param ('password');
    # create the script
    if (open (OUT, ">$file")) {
	print OUT "#!/bin/sh\n";
	if ($encrypt eq "on") {
	    # store the password
	    my ($pwdir, $filename, $fh);
	    $pwdir = "/var/packages/autorun/target/passwords";
	    mkdir $pwdir unless -d $pwdir;
	    ($fh, $filename) = tempfile (DIR => $pwdir);
	    print $fh "$password";
	    close ($fh);
	    $filename = substr ($filename, length ($pwdir) + 1, length ($filename) - length ($pwdir) - 1);
	    print OUT "/var/packages/autorun/target/encryptbackup \"$filename\" \"$backup\" \"$target\" \"\$1\" ";
	} else {
	    print OUT "/var/packages/autorun/target/localbackup \"$backup\" \"$target\" \"\$1\" ";
	}
	if ($eject eq "on") {
	    print OUT "100";
	} else {
	    print OUT "0";
	}
	if ($encrypt eq "on") {
	    if ($encryptfilename eq "on") {
		print OUT " \"y\"";
	    } else {
		print OUT " \"n\"";
	    }
	}
	print OUT "\nexit \$?\n";
	close (OUT);
	chmod 777, $file;
    }
}
if ($action eq "delete") {
    $file = param ('file');
    unlink ($file);
}

# find the mounted devices
if (open (IN,"/bin/mount 2>&1 |")) {
    while(<IN>) {
	@tmp = split (" ");
	if ((substr (@tmp[2], 0, 10) eq "/volumeUSB") || (substr (@tmp[2], 0, 11) eq "/volumeSATA")) {
	    $text = " action=\"localbackup.cgi\" method=\"post\">\n\t\t\t\t<input type=\"hidden\" name=\"action\" value=\"create\" />\n\t\t\t\t<input type=\"hidden\" name=\"file\" value=\"@tmp[2]/$tmplhtml{'SCRIPT'}\" />\n\t\t\t\t<input type=\"hidden\" name=\"target\" value=\"@tmp[2]\" />\n\t\t\t\t<td><input type=\"text\" size=\"15\" name=\"backup\" /></td>\n\t\t\t\t<td></td>\n\t\t\t\t<td>@tmp[2]</td>\n\t\t\t\t<td></td>\n\t\t\t\t<td align=\"center\"><input type=\"checkbox\" name=\"eject\" /></td>\n\t\t\t\t<td></td>\n\t\t\t\t<td align=\"center\"><input type=\"checkbox\" name=\"encrypt\" /></td>\n\t\t\t\t<td></td>\n\t\t\t\t<td align=\"center\"><input type=\"text\" size=\"15\" name=\"password\" /></td>\n\t\t\t\t<td></td>\n\t\t\t\t<td align=\"center\"><input type=\"checkbox\" name=\"encryptfilename\" /></td>\n\t\t\t\t<td></td>\n\t\t\t\t<td>\n\t\t\t\t<td><input type=\"submit\" value=\"  Create  \"";
	    if (-e "@tmp[2]/$tmplhtml{'SCRIPT'}") {
		$text = "<form onsubmit=\"return commitOverwrite(\'@tmp[2]/$tmplhtml{'SCRIPT'}\')\"$text /></td>\n\t\t\t</form>\n\t\t\t<form action=\"localbackup.cgi\" method=\"post\" onsubmit=\"return commitDelete(\'@tmp[2]/$tmplhtml{'SCRIPT'}\')\">\n\t\t\t\t<input type=\"hidden\" name=\"action\" value=\"delete\" />\n\t\t\t\t<input type=\"hidden\" name=\"file\" value=\"@tmp[2]/$tmplhtml{'SCRIPT'}\" />\n\t\t\t\t<td><input type=\"submit\" value=\"  Delete  \" /></td>\n\t\t\t</form>";
	    } else {
		$text = "<form $text /></td><td></td>\n";
	    }
	    $tmplhtml{'BACKUPS'} = "$tmplhtml{'BACKUPS'}\t\t<tr height=\"27\">\n\t\t\t$text\n\t\t\t</form>\n\t\t</tr>\n";
	}
    }
    close(IN);
}

# output
if (open (IN, "localbackup.htmlt")) {
    while (<IN>) {
	s/==:([^:]+):==/$tmplhtml{$1}/g;
	print $_;
    }
    close (IN);
}
