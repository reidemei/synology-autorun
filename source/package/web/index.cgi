#!/usr/bin/perl -w

use CGI qw/:standard/;
use CGI::Carp qw(fatalsToBrowser);

print "Content-type: text/html\n\n";

# check authentication
if (open (IN,"/usr/syno/synoman/webman/modules/authenticate.cgi|")) {
    $user=<IN>;
    chop($user);
    close(IN);
}
if ($user ne "admin") {
    print "<HTML><HEAD><TITLE>Login Required</TITLE></HEAD><BODY>Please login as admin first, before using this webpage<br/><br/></BODY></HTML>\n";
    die;
}

# default values 
$tmplhtml{'saved'}="";
$tmplhtml{'SCRIPT'}="autorun";
$tmplhtml{'BEEP'}=" checked ";
$tmplhtml{'LED'}=" checked ";
$tmplhtml{'NOTIFY'}=" checked ";
$tmplhtml{'NOTIFYTARGET'}="admin";

# shall we save?
$action=param ('action');
if ($action eq "save") {
    if (open (OUT, ">/var/packages/autorun/target/config")) {
	$script=param ('script');
	$beep=param ('beep');
	$led=param ('led');
        $notify=param ('notify');
        $notifytarget=param ('notifytarget');
	print OUT "SCRIPT=$script\n";
	if ($beep eq "on") {
	    print OUT "BEEP=1\n";
	} else {
	    print OUT "BEEP=0\n";
	}
	if ($led eq "on") {
	    print OUT "LED=1\n";
	} else {
	    print OUT "LED=0\n";
	}
        if ($notify eq "on") {
            print OUT "NOTIFY=1\n";
        } else {
            print OUT "NOTIFY=0\n";
        }
        print OUT "NOTIFYTARGET=$notifytarget\n";
	close (OUT);
	$tmplhtml{'saved'}=" <small style=\"color:green;\">(saved)</small>";
    } else {
	$tmplhtml{'saved'}=" <small style=\"color:red;\">(unable to save the config)</small>";
    }
}

# shall we reset the led?
if ($action eq "resetled") {
    if (open (OUT, ">/dev/ttyS1")) {
	print OUT "8";
	close (OUT);
    }
}

# (re-)read the configuration
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
    if ($tmplhtml{'BEEP'} eq "1") {
	$tmplhtml{'BEEP'} = "checked=\"checked\"";
    } else {
	$tmplhtml{'BEEP'} = "";
    }
    if ($tmplhtml{'LED'} eq "1") {
	$tmplhtml{'LED'} = "checked=\"checked\"";
    } else {
	$tmplhtml{'LED'} = "";
    }
    if ($tmplhtml{'NOTIFY'} eq "1") {
        $tmplhtml{'NOTIFY'} = "checked=\"checked\"";
    } else {
        $tmplhtml{'NOTIFY'} = "";
    }
} else {
    $tmplhtml{'saved'}=" <small style=\"color:red;\">(unable to load the config)</small>";
}

# clear the log file?
if ($action eq "clearlog") {
    if (open (OUT, ">/var/packages/autorun/target/log")) {
	my ($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime(time);
	$year += 1900; ## $year contains no. of years since 1900, to add 1900 to make Y2K compliant
	$dt = sprintf ("%04s-%02s-%02s %02s:%02s:%02s", $year, $mon, $mday, $hour, $min, $sec);
	print OUT "$dt: log file cleared<br/>\n";
	close (OUT);
    }
    $action = "log"
}

# shall we display the log?
if ($action eq "log") {
    if (open (IN, "log.html")) {
	while (<IN>) {
	    s/==:([^:]+):==/$tmplhtml{$1}/g;
	    print $_;
	}
	close (IN);
	if (open (IN, "/var/packages/autorun/target/log")) {
	    while (<IN>) {
		print $_;
	    }
	    close (IN);
	}
	print "</code>\n</p>\n</body>\n</html>";
    }
} else {
    # print html page
    if (open (IN, "index.htmlt")) {
	while (<IN>) {
	    s/==:([^:]+):==/$tmplhtml{$1}/g;
	    print $_;
	}
	close (IN);
    }
}
