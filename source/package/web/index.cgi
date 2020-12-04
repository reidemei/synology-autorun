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

# header
print '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">', "\n";
print "<html><head><title>autorun</title></head><body>\n";

# description
print "<h3>Description</h3>\n";
print "<p><b>autorun</b> allows to execute scripts when an external device (USB + eSATA) is connected to the DiskStation.<br/>\n";
print "To enable it start the package via the \"<i>Package Management</i>\". The log file can be viewed there too (\"<i>Show info</i>\" - \"<i>Protocol</i>\").<br/>\n";
print "When a device is connected to the DiskStation and successfully mounted the configured script (located on the device) will be executed. An exit value of \"100\" of the script will unmount and eject the device, all other values will leave it mounted.</p>\n";

# configuration
print "<h3>Configuration";

# shall we save?
$action=param ('action');
if ($ENV{'REQUEST_METHOD'} eq "POST") {
    if (open (OUT, ">/var/packages/autorun/target/config")) {
	$script=param ('script');
	$beep=param ('beep');
	$led=param ('led');
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
	close (OUT);
	print " <small style=\"color:green;\">(saved)</small>";
    } else {
	print " <small style=\"color:red;\">(unable to save the config)</small>";
    }
}

# (re-)read the configuration
$conf_script="autorun";
$conf_beep="1";
$conf_led="1";
if (open (IN, "/var/packages/autorun/target/config")) {
    while (<IN>) {
	chomp;
	s/#.//;
	s/^\s+//;
	s/\s+$//;
	my ($var, $value) = split(/\s*=\s*/, $_, 2);
	if ($var eq "SCRIPT") {
	    $conf_script=$value;
	}
	if ($var eq "BEEP") {
	    $conf_beep=$value;
	}
	if ($var eq "LED") {
	    $conf_led=$value;
	}
    }
    close (IN);
} else {
    print " <small style=\"color:red;\">(unable to load the config)</small>";
}

# form
print "</h3>\n";
print "<form action=\"index.cgi\" method=\"post\">\n";
print "<table border=\"0\">\n";
print "<tr><td><b>Script to execute:</b></td><td width=\"10\"></td><td><input type=\"text\" name=\"script\" size=\"25\" value=\"$conf_script\"/></td><td width=\"200px\"></td></tr>\n";
print "<tr><td colspan=\"4\"><small>&nbsp;&nbsp;&nbsp;The script must be located in the root directory of the device and set as executable for the user \"root\".</small></td></tr>\n";
print "<tr><td><b>Beep at the start and end:</b></td><td></td><td><input type=\"checkbox\" name=\"beep\"/";
if ($conf_beep eq "1") {
    print " checked ";
}
print "></td><td></td></tr>\n";
print "<tr><td><b>Use status LED:</b></td><td></td><td><input type=\"checkbox\" name=\"led\"";
if ($conf_led eq "1") {
    print " checked ";
}
print "/></td><td></td></tr>\n";
print "<tr><td colspan=\"4\"><small>&nbsp;&nbsp;&nbsp;When enable the status LED will switch to orange while the script is running. You can savely remove<br/>&nbsp;&nbsp;&nbsp;the device when it goes green again (and the script triggered an eject).</small></td></tr>\n";
print "<input type=\"hidden\" name=\"action\" value=\"save\"/>\n";
print "<td></td><td></td><td align=\"right\">\n";
print "<input type=\"reset\" value=\"  Reset  \"/>\n";
print "<input type=\"submit\" value=\"  Save  \"/>\n";
print "</td><td></td></tr>\n";
print "</table>\n";
print "</form>\n";

# limitations
print "<h3>Limitations</h3>\n";
print "<ul>\n<li>Multiple executions (two or more devices at the same time) are possible but the status display via the LED will not properly reflect it.</li>\n";
print "<li>There is no error handling for the called scripts.</li>\n";
print "<li>Scripts might also be called during system boot-up when some resources are not be available.</li>\n";
print "<li>Problems while unmounting the device will be signaled with three long beeps. The status LED will be left orange (if enabled) so you have to reset it yourself (<code>echo 8 > /dev/ttyS1</code>).</li>\n</ul>\n";

# license
print "<h3>License <small>(BSD)</small></h3>\n";
print "<p><small>Copyright (c) 2011, Jan Reidemeister<br/>\n";
print "All rights reserved.<br/><br/>\n";
print "Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:\n";
print "<ul>\n<li>Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.</li>\n";
print "<li>Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.</li>\n";
print "<li>Neither the name of Jan Reidemeister nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.</li>\n</ul>\n";
print "THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS \"AS IS\" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.<br/><br/>\n";
print "Icon from <a href=\"http://openiconlibrary.sourceforge.net\">Open Icon Library</a> (Nuvola 1.0, LGPL-2.1).</small></p>\n";

# end
print "</body></html>\n";
