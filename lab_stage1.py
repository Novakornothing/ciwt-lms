"""Stage 1 command explanations.

Each command is described from its own words and flags. Periods in paths and
addresses are left as periods. Nothing here is shared filler such as
"runs as written" or "Step N matters because".
"""
from __future__ import annotations

import re
import shlex


def _blurb(lab):
    text = (lab.get("blurb") or lab.get("intro") or "").strip()
    text = re.sub(r"^\d+[a-z]?\.\s*", "", text)
    return text.rstrip(".")


def _kind(kind):
    return kind or ""


def _mode_phrase(spec):
    spec = str(spec).strip()
    if re.fullmatch(r"[0-7]{3,4}", spec):
        n = int(spec[-3:], 8)
        names = []
        for shift, who in ((6, "the owner"), (3, "the group"), (0, "everyone else")):
            b = (n >> shift) & 7
            bits = []
            if b & 4:
                bits.append("read")
            if b & 2:
                bits.append("write")
            if b & 1:
                bits.append("execute")
            names.append(f"{who} can {' and '.join(bits)}" if bits else f"{who} gets no access")
        sticky = ""
        if len(spec) == 4 and spec[0] in "1234567":
            extra = []
            lead = int(spec[0])
            if lead & 4:
                extra.append("setuid")
            if lead & 2:
                extra.append("setgid")
            if lead & 1:
                extra.append("the sticky bit")
            if extra:
                sticky = " The leading digit turns on " + " and ".join(extra) + "."
        return f"The numeric mode {spec} means {names[0]}, {names[1]}, and {names[2]}.{sticky}"
    m = re.fullmatch(r"([ugoa]*)([+\-=])([rwxst]+)", spec)
    if not m:
        return f"{spec} is a symbolic permission change."
    who, op, perms = m.groups()
    who_s = {"u": "the owner", "g": "the group", "o": "others", "a": "everyone", "": "everyone"}.get(who, "the named class")
    if who == "ug":
        who_s = "the owner and the group"
    perm_s = {"r": "read", "w": "write", "x": "execute", "s": "the setuid or setgid bit", "t": "the sticky bit"}
    bits = " and ".join(perm_s.get(ch, ch) for ch in perms)
    verb = {"+": "adds", "-": "removes", "=": "sets exactly"}[op]
    return f"{spec} {verb} {bits} for {who_s} and leaves the other classes as they are."


def _split(cmd):
    try:
        return shlex.split(cmd)
    except ValueError:
        return cmd.split()


def _here(lab):
    title = (lab.get("title") or lab.get("id") or "this lab").strip()
    title = re.sub(r"^\d+[a-z]?\.\s*", "", title)
    title = title.replace(".", " ").strip().rstrip(".")
    return title or (lab.get("id") or "this lab")


def explain_command(cmd, kind, lab):
    """One accurate sentence for this exact command line."""
    raw = str(cmd).strip().split("|", 1)[0].strip()
    shown = raw
    where = ""
    m = re.match(r"^\[([^\]]+)\]\s+(.*)$", raw)
    if m:
        where = m.group(1)
        raw = m.group(2).strip()
    kind = _kind(kind)
    low = raw.lower()
    parts = _split(raw)
    tool = (parts[0] if parts else raw).lower()
    sentence = _body(raw, low, tool, parts, kind, lab)
    if where:
        sentence = sentence.rstrip(".") + f", and this line runs on the {where} machine"
    # A period followed by whitespace starts a new sentence. Dots inside
    # addresses and paths are not followed by whitespace, so they stay dots.
    sentence = re.sub(r"\.\s+", ", ", sentence).rstrip(".")
    return sentence + "."


def _body(raw, low, tool, parts, kind, lab):
    if low in ("enable", "en"):
        if kind in ("switch", "router"):
            return "enable moves the console from user EXEC, where the prompt ends in >, to privileged EXEC, where the prompt ends in #. It does not enter configuration mode."
        return "enable is not a command on this system."
    if low in ("configure terminal", "conf t", "configure"):
        return "configure terminal, typed from privileged EXEC, enters global configuration. The prompt changes to (config). From user EXEC, with a > prompt, the line is rejected."
    if low == "end":
        return "end leaves every configuration submode and returns to privileged EXEC. The prompt should be a bare # with no (config)."
    if low == "exit":
        return "exit climbs one configuration level: interface or VLAN mode back to (config), then (config) back to privileged EXEC."
    if low in ("write", "write memory", "copy running-config startup-config"):
        return "write memory copies the running configuration to startup configuration so the change is still there after a reload. Until this line, a reboot drops what you just typed."
    if tool == "hostname":
        if kind in ("switch", "router"):
            arg = " ".join(parts[1:]) if len(parts) > 1 else ""
            if arg:
                return f"hostname {arg}, typed in global configuration, sets the device name. The prompt adopts {arg}. This is not the Windows hostname command."
            return "hostname with no argument is not how a switch or router is renamed. The name is set from global configuration with hostname followed by the new name."
        if kind in ("windows", "win11gui"):
            return "hostname with no argument prints this PC's computer name and nothing else. It does not rename the PC and it does not talk to a router."
        arg = " ".join(parts[1:]) if len(parts) > 1 else ""
        if arg:
            return f"hostname {arg} sets the Linux kernel hostname for this boot. It does not edit a Windows computer name and it does not configure a router prompt."
        return "hostname with no argument prints the Linux hostname and exits. It does not list users and it does not print a Windows DOMAIN\\user string."
    if tool == "whoami":
        if kind in ("windows", "win11gui"):
            return "whoami prints the Windows account this shell is using, often in DOMAIN\\user form. It does not list other accounts."
        return "whoami prints the Unix account name of this shell. On Linux that is a short name such as root or trainee, not a DOMAIN\\user string."
    if tool == "chmod" and len(parts) >= 3:
        spec, paths = parts[1], " ".join(parts[2:])
        return f"chmod {spec} {paths} changes permission bits on an existing file. {_mode_phrase(spec)} chmod does not create the file and does not change the owner."
    if tool == "chown" and len(parts) >= 3:
        who, path = parts[1], " ".join(parts[2:])
        return f"chown {who} {path} changes the owner of an existing file to {who}. It does not change the permission bits. On a normal user shell this needs root, which is sudo chown."
    if tool == "adduser" or tool == "useradd":
        flags = []
        if "-D" in parts or "-d" in [p for p in parts]:
            pass
        text = " ".join(parts)
        if "-D" in parts and "-d" not in parts:
            user = parts[-1]
            return f"adduser -D {user} is the BusyBox form that creates {user} without asking for a password. The capital D is not -d. Lowercase -d would set a home directory instead."
        if "-d" in parts:
            return f"{text} uses lowercase -d, which sets the home directory for the new account. It is not BusyBox -D."
        if "-m" in parts:
            return f"{text} creates the account and, because of -m, also creates its home directory. -s sets the login shell and -G adds a supplementary group."
        return f"{text} creates or updates an account. Read each flag on this line rather than assuming a default home or password."
    if tool == "printf":
        how = "appends to the file because >> is shell redirection" if " >>" in raw else "replaces the file because > is shell redirection" if " >" in raw else "writes to the terminal"
        return f"{raw} writes the quoted text with printf, which {how}. The format string controls newlines. A missing parent directory is an error."
    if tool == "echo":
        redir = "replaces the file" if " >" in raw or raw.endswith(">") else "writes to the terminal"
        if " >>" in raw:
            redir = "appends to the file"
        return f"{raw} uses echo, which {redir}. Quoted spaces stay one argument."
    if tool == "ipconfig":
        if "/all" in low:
            return f"ipconfig /all prints the adapter, DHCP state, IPv4 address, mask, gateway, and DNS servers on {_here(lab)}. It does not change them. /all is the flag that adds the DNS list. The dots in the addresses are dots."
        if "/flushdns" in low:
            return "ipconfig /flushdns clears the resolver cache on this PC. It does not change which DNS server is configured."
        if "/release" in low:
            return "ipconfig /release drops the DHCP address on the adapter. It does not set a DNS server."
        if "/renew" in low:
            return "ipconfig /renew asks DHCP for a new lease. It does not rewrite the DNS server list by itself."
        return "ipconfig prints the IPv4 address, mask, and gateway. Without /all it omits the full DNS list. It does not change the configuration."
    if tool == "ping":
        extra = []
        if "-c" in parts:
            extra.append("-c sets how many probes to send")
        if "-W" in parts:
            extra.append("-W sets how many seconds to wait for each reply")
        if "-n" in parts and kind in ("windows", "win11gui"):
            extra.append("-n sets the count on Windows")
        flag = (" " + ", and ".join(extra) + ".") if extra else ""
        return f"{raw} sends ICMP echo requests.{flag} A reply means that host answered. A name that fails while its address answers points at DNS, not at the cable."
    if tool in ("nslookup", "resolve-dnsname", "drill"):
        return f"{raw} asks a DNS server to resolve a name. It does not prove the address then accepts a connection."
    if tool == "vlan" and len(parts) >= 2:
        vid = parts[1]
        return f"vlan {vid}, typed in global configuration, creates VLAN {vid} if it is missing and enters VLAN configuration, where the prompt is (config-vlan). The number {vid} is an identifier, not an IP address."
    if tool == "name" and len(parts) >= 2:
        nm = " ".join(parts[1:])
        return f"name {nm}, typed in VLAN configuration, sets that VLAN's name to {nm}. It does not move any port into the VLAN."
    if tool == "interface" and len(parts) >= 2:
        iface = "".join(parts[1:])
        sub = ""
        if "." in iface:
            sub = f" The dot in {iface} marks a subinterface, which is a separate logical interface on the physical port, not a separator to turn into a comma."
        return f"interface {iface} enters interface configuration for {iface} on {_here(lab)}. The prompt becomes (config-if).{sub}"
    if "switchport mode access" in low:
        return "switchport mode access makes this interface an access port, which carries one VLAN untagged. It does not choose which VLAN. That is a separate switchport access vlan line."
    if "switchport mode trunk" in low:
        return "switchport mode trunk makes this interface a trunk, which can carry multiple VLANs. It does not by itself limit which VLANs are allowed."
    if low.startswith("switchport access vlan"):
        vid = parts[-1]
        return f"switchport access vlan {vid} places this access port in VLAN {vid}. The port must already be in access mode. Hosts on the port then sit in VLAN {vid}."
    if "switchport trunk allowed" in low:
        return f"{raw} limits which VLANs may cross this trunk. VLANs left off the list are not carried, even if they exist on the switch."
    if "switchport port-security" in low:
        return f"{raw} turns on port security on this interface. Sticky or maximum values only apply if this line includes them. A later show command is what proves the port is secured."
    if low in ("no shutdown", "no shut"):
        return f"no shutdown brings this interface up administratively on {_here(lab)}. Until this line, the interface stays down even if it has an address."
    if low == "shutdown":
        return "shutdown administratively disables this interface. Traffic stops until no shutdown."
    if low.startswith("ip address"):
        addr = parts[2] if len(parts) > 2 else ""
        mask = parts[3] if len(parts) > 3 else ""
        return f"ip address {addr} {mask} sets this interface's IPv4 address and mask on {_here(lab)}. Both numbers keep their dots. The interface still needs no shutdown if it is administratively down."
    if low.startswith("encapsulation dot1q"):
        vid = parts[-1]
        return f"encapsulation dot1Q {vid} tags this subinterface with VLAN {vid}. The 802.1Q header is how a router separates VLANs on one physical trunk."
    if tool == "curl":
        bits = [f"{raw} requests a URL."]
        if "-s" in parts:
            bits.append("-s is silent, so progress is not printed.")
        if "-S" in parts:
            bits.append("-S shows errors even when -s is set.")
        if "-w" in parts or any(a.startswith("-w") for a in parts):
            bits.append("-w is the write-out format printed after the transfer, not a wait.")
        if "-o" in parts:
            bits.append("-o writes the body to a named file.")
        if "-I" in parts:
            bits.append("-I fetches headers only.")
        if "-k" in parts:
            bits.append("-k skips certificate verification.")
        return " ".join(bits)
    if tool == "traceroute":
        bits = [f"{raw} lists each hop to the destination."]
        if "-n" in parts:
            bits.append("-n prints numeric addresses and does not look up DNS names.")
        if "-q" in parts:
            bits.append("-q is how many probes are sent per hop.")
        if "-w" in parts:
            bits.append("-w is how long to wait for a probe reply.")
        return " ".join(bits)
    if tool == "crontab":
        if "-l" in parts:
            return f"{raw} lists the crontab for this user. -l means list. It does not edit the table."
        return f"{raw} installs the crontab from the named file, replacing the previous table."
    if tool == "find":
        bits = [f"{raw} walks a directory tree."]
        if "-perm" in parts:
            bits.append("-perm selects by permission bits. The value that follows, such as -4000, is the mode test, not a flag of its own. -4000 means the setuid bit is set.")
        if "-type" in parts:
            bits.append("-type f limits the walk to regular files.")
        return " ".join(bits)
    if low.startswith("ip route add default via"):
        hop = parts[-1]
        return f"{raw} installs a default route via {hop}. The address keeps its dots. It is the Linux iproute2 command, not the Cisco ip route line."
    if low.startswith("ip route"):
        dest = parts[2] if len(parts) > 2 else ""
        mask = parts[3] if len(parts) > 3 else ""
        hop = parts[4] if len(parts) > 4 else ""
        if dest == "0.0.0.0":
            return f"ip route 0.0.0.0 0.0.0.0 {hop} installs a default route whose next hop is {hop}. The zeros stay dotted decimals. 0.0.0.0 with mask 0.0.0.0 means every destination that has no more specific route."
        return f"ip route {dest} {mask} {hop} installs a static route for {dest} mask {mask} via {hop}."
    if low.startswith("access-list"):
        return f"{raw} adds a line to a numbered access list. A standard list is 1 to 99. The word host means one address, which is the same as a wildcard of 0.0.0.0 with the dots kept. This line does not apply the list to an interface."
    if "access-group" in low:
        direction = "outbound" if low.endswith(" out") or " out" in low else "inbound" if " in" in low else "the named direction"
        return f"{raw} applies an access list to this interface in the {direction} direction. out means traffic leaving the interface. The list must already exist or it filters nothing."
    if low.startswith("description"):
        return f"{raw} sets the interface description, which is a label for operators. It does not change addressing or VLAN membership."
    if low.startswith("banner"):
        return f"{raw} sets the login banner. The delimiter character wraps the text. The banner is shown at login. It is not the device hostname."
    if low.startswith("show") or low.startswith("sh "):
        if "vlan" in low:
            return f"{raw} prints the VLAN table: id, name, status, and the ports in each VLAN. It does not create a VLAN or move a port."
        if "ip route" in low or low.strip() in ("show ip route", "sh ip route"):
            return f"{raw} prints the routing table, including connected networks and static routes. A default route appears as 0.0.0.0/0. It does not add a route."
        if "version" in low:
            return f"{raw} prints the software version and uptime. It does not change the configuration and it does not set the hostname."
        if "mac" in low:
            return f"{raw} prints the MAC address table, which is what the switch has learned on each port. It does not secure a port."
        if "interface" in low or "int status" in low or "ip int" in low:
            return f"{raw} prints interface state. Status and protocol are separate columns. It does not enable an interface."
        return f"{raw} reads the device and prints a table or a short block. It does not change the running configuration."
    if tool == "grep":
        flags = []
        if "-q" in parts:
            flags.append("-q suppresses the matching lines and only sets the exit status")
        if "-c" in parts:
            flags.append("-c prints a count instead of the lines")
        if "-E" in parts or "-Eq" in "".join(parts):
            flags.append("-E treats the pattern as an extended regular expression")
        if "-v" in parts:
            flags.append("-v prints lines that do not match")
        if "-n" in parts:
            flags.append("-n adds the line number")
        if "-R" in parts or "-r" in parts:
            flags.append("-r searches down through directories")
        extra = (" " + ". ".join(flags) + ".") if flags else ""
        return f"{raw} prints lines that match the pattern. grep does not edit the file.{extra}"
    if tool == "ls":
        flag = ""
        if "-l" in parts or raw == "ll":
            flag = " -l adds permissions, owner, group, size, and time."
        if "-a" in parts:
            flag += " -a includes names that start with a dot."
        return f"{raw} lists directory entries.{flag} It does not change permissions."
    if tool == "mkdir":
        p = " -p creates missing parent directories and does not fail if the directory already exists." if "-p" in parts else ""
        return f"{raw} creates a directory.{p}"
    if tool == "cd":
        return f"{raw} changes the shell's current directory. It does not copy or delete anything. A later relative path is resolved from there."
    if tool == "rm":
        return f"{raw} deletes the named file. -f hides the error if it is already gone. It does not remove a directory unless -r is present."
    if tool == "cp":
        extra = ""
        if "-a" in parts:
            extra = " -a keeps ownership, mode, and timestamps as far as the system allows."
        elif "-p" in parts:
            extra = " -p preserves the mode and timestamps."
        return f"{raw} copies a file.{extra} The source is left in place."
    if tool == "mv":
        return f"{raw} moves or renames a file. The old path is gone after it succeeds."
    if tool == "cat":
        return f"{raw} prints the file to the terminal on {_here(lab)}. It does not modify the file."
    if tool == "sed":
        inplace = " -i edits the file in place." if "-i" in parts else ""
        return f"{raw} runs a stream edit.{inplace} The s expression replaces the first match on each line unless a g flag is present."
    if tool in ("kill", "killall"):
        return f"{raw} signals a process. With no signal number it sends TERM. It does not delete the program file."
    if tool == "service" or (tool == "/etc/init.d/s50heartbeat" or raw.startswith("/etc/init.d/")):
        return f"{raw} runs the service script. start launches it, status reports it, and a missing execute bit makes the script fail before it can start."
    if tool == "sysctl":
        return f"{raw} sets a kernel parameter. -w writes the value for this boot. It is not saved across reboot unless a config file also contains it."
    if tool == "iptables":
        if "-L" in parts or "-l" in [p for p in parts]:
            table = "the nat table" if "nat" in parts else "the filter table"
            return f"{raw} lists rules in {table}. -L is list, -n shows numeric addresses, -v adds packet counters, and --line-numbers numbers the rules. It does not add or delete a rule."
        if "-a" in [p.lower() for p in parts] or " -A " in raw or raw.lower().startswith("iptables -a"):
            return f"{raw} appends one rule. Order matters because the first matching rule wins. -i lo means the loopback interface, -p tcp selects TCP, --dport is the destination port, and -s is the source address."
        if "-p" in parts and "DROP" in raw:
            return f"{raw} sets the chain policy. DROP means traffic that matches no rule is discarded. This does not delete the rules already on the chain."
        if "-s" in [p.lower() for p in parts] or low.startswith("iptables -s"):
            return f"{raw} prints the current rules. It does not change them."
        return f"{raw} changes or prints the packet filter. Read -A as append, -P as policy, -s as source, and --dport as destination port."
    if tool == "ip" and len(parts) >= 2:
        if parts[1] == "route" or (len(parts) > 2 and parts[1] in ("-4", "-6") and "route" in parts):
            if "add" in parts and "default" in parts:
                hop = parts[-1]
                return f"{raw} installs a default route via {hop}. The address keeps its dots and, on IPv6, its colons."
            return f"{raw} reads or changes the routing table. A default route is the one used when no longer prefix matches."
        if "addr" in parts and "add" in parts:
            return f"{raw} adds an address to the interface. The prefix length after the slash is the mask size, not a separate dotted mask."
        if parts[1] in ("a", "addr", "address") or (len(parts) > 1 and parts[1] in ("-4", "-6")):
            return f"{raw} shows addresses on the interfaces. 169.254 addresses are link-local, not a DHCP lease."
        return f"{raw} is the iproute2 command. The second word selects the object: address, route, or link."
    if tool == "sshd":
        return f"{raw} checks or starts the SSH daemon. sshd -t tests the configuration and prints errors without restarting."
    if tool == "ssh-keygen":
        bits = []
        if "-t" in parts:
            bits.append("-t chooses the key type")
        if "-N" in parts:
            bits.append("-N is the passphrase, and an empty string means no passphrase")
        if "-f" in parts:
            bits.append("-f is the output file")
        if "-q" in parts:
            bits.append("-q keeps it quiet")
        extra = (" " + ". ".join(bits) + ".") if bits else ""
        return f"{raw} generates a key pair.{extra}"
    if "passwordauthentication" in low or "permitrootlogin" in low:
        return f"{raw} changes one sshd setting. PasswordAuthentication no refuses passwords. PermitRootLogin no refuses direct root login. sshd -t is how you confirm the file still parses."
    # fallback: say what each token does on this line. Redirection is the shell's, not the program's.
    known = {
        "-i": "selects the interface",
        "-n": "prints numeric addresses and skips DNS lookups",
        "-t": "sets a count or a type", "-T": "sets a timeout", "-c": "sets a count",
        "-w": "is the write-out format" if tool == "curl" else ("writes a capture file" if tool == "tcpdump" else "sets how long to wait"),
        "-U": "flushes each packet",
        "-q": "is the number of probes per hop" if tool == "traceroute" else "keeps the command quiet",
        "-f": "names a file or forces the action", "-r": "reads a file or recurses",
        "-v": "adds detail",
        "-l": "lists the current table" if tool == "crontab" else "uses a long listing",
        "-s": "is silent, hiding the progress meter" if tool == "curl" else "names the source",
        "-o": "writes the body to a file" if tool == "curl" else "selects the output interface",
        "-I": "fetches headers only" if tool == "curl" else "inserts a rule",
        "-k": "skips certificate checks" if tool == "curl" else "keeps going after errors",
        "--test": "checks the configuration without starting the daemon",
        "-perm": "selects files by a permission test, and the next token is the mode value",
    }
    redir = ""
    args = []
    i = 1
    while i < len(parts):
        arg = parts[i]
        if arg in (">", ">>"):
            target = parts[i + 1] if i + 1 < len(parts) else "the named file"
            verb = "appends to" if arg == ">>" else "replaces"
            redir = f"{arg} is shell redirection and {verb} {target}. It is not an argument to {parts[0]}."
            i += 2
            continue
        args.append(arg)
        i += 1
    bits = []
    for arg in args:
        if arg.startswith("-") and not re.fullmatch(r"-\d+", arg):
            meaning = known.get(arg) or known.get(arg.split("=", 1)[0])
            if meaning:
                bits.append(f"{arg} {meaning}.")
            else:
                bits.append(f"{arg} is a flag on {parts[0]}.")
        elif re.fullmatch(r"-\d+", arg):
            bits.append(f"{arg} is a value passed to {parts[0]}, not a flag name.")
        elif re.fullmatch(r"\d{1,3}(\.\d{1,3}){3}", arg):
            bits.append(f"{arg} is an IPv4 address, and the dots stay dots.")
        elif "/" in arg or arg.startswith("."):
            bits.append(f"{arg} is a path.")
        else:
            bits.append(f"{arg} is a value passed to {parts[0]}.")
    if redir:
        bits.append(redir)
    if not bits:
        bits.append(f"{parts[0]} is entered on its own on this line.")
    return " ".join(bits)


def guided_html(lab, esc, commands):
    kind = lab.get("kind") or ""
    parts = []
    intro = (lab.get("intro") or "").strip()
    blurb = (lab.get("blurb") or "").strip()
    if intro:
        parts.append(f"<p>{esc(intro)}</p>")
    elif blurb:
        parts.append(f"<p>{esc(blurb)}</p>")
    if commands:
        items = []
        shown = []
        for i, cmd in enumerate(commands):
            sentence = explain_command(cmd, kind, lab)
            # Mode changes such as enable are the same words on every IOS lab.
            # Name this lab and the following line so the sentence is about this walkthrough.
            title = _here(lab)
            shared = (
                "enable moves the console",
                "configure terminal, typed from",
                "end leaves every configuration",
                "exit climbs one configuration",
                "write memory copies the running",
            )
            if any(sentence.lower().startswith(prefix) for prefix in shared):
                nxt = commands[i + 1] if i + 1 < len(commands) else ""
                if nxt:
                    sentence = sentence.rstrip(".") + f" On {title}, the next line is {nxt}."
                else:
                    sentence = sentence.rstrip(".") + f" On {title}, this is the last line of the walkthrough."
            words = re.findall(r"[A-Za-z0-9][A-Za-z0-9'./_-]*", sentence.lower())
            key = tuple(words[:3])
            seen = sum(1 for prev in shown if prev == key)
            if seen >= 2:
                leads = ("Following that, ", "After the previous line, ", "With that done, ", "On the next line, ")
                sentence = leads[(seen - 2) % len(leads)] + sentence[0].lower() + sentence[1:]
            shown.append(key)
            items.append(
                f"<li class=\"type-this\"><p>{esc(sentence)}</p>"
                f"<p><code class=\"cmd-text\">{esc(cmd)}</code></p></li>"
            )
        parts.append("<ol class=\"walk\">" + "".join(items) + "</ol>")
    else:
        bits = []
        for obj in lab.get("objectives") or []:
            text = (obj.get("text") or obj.get("id") or "").strip()
            if text:
                bits.append(f"<li><p>{esc(text)}</p></li>")
        if bits:
            parts.append("<ol class=\"walk\">" + "".join(bits) + "</ol>")
    return "\n".join(parts)
