"""Pass 15: option-length parity for the chapter checks (ITSUP Q*, reused by CLIENT; NETOPS NQ*).

In 108 of 200 chapter-check items the key was uniquely the longest option, often by 10+ characters: a test-wise
cue. Here one or two distractors per item are rewritten to a similar length by adding plausible detail, without
changing what makes them wrong. A few keys are tightened. Meaning, keys and option order are unchanged; only text
is replaced, in place. Misconception tags follow the rewritten distractor (see curriculum_v2/misconceptions.py).
Written by Grok Bot; Pending SME review.

REWRITE[bank_id] = {old option text: new option text}. Applied after the item review (ITSUP) and in
netops_quiz_payload (NETOPS); a test fails if an old text is not found."""

REWRITE = {
    # ---------------------------------------------------------------- ITSUP chapter 1
    'Q1.3': {'Hotel Wi-Fi is bad, told the user to find a better network and call back later':
             'Hotel Wi-Fi is bad, so I told the user to find a better network and to call us back later today'},
    'Q1.4': {'Open the case first, then unplug it': 'Open the case first, then unplug it at the wall'},
    'Q1.9': {'The monitoring icon turned green': 'The monitoring icon for the service turned green again'},
    # ---------------------------------------------------------------- chapter 2
    'Q2.5': {'After Windows signs in, to load drivers': 'After Windows signs in, to load the device drivers'},
    'Q2.6': {'It encrypts the system drive': 'It encrypts the system drive against theft'},
    'Q2.8': {'SYS_FAN, the chassis-fan header': 'SYS_FAN, the chassis-fan header on the board'},
    'Q2.9': {'Run Windows Update, then recheck': 'Run Windows Update, then recheck About'},
    # ---------------------------------------------------------------- chapter 3
    'Q3.0': {'A form factor equal to ATX': 'A board form factor, the same as ATX'},
    'Q3.6': {'Replace the motherboard': 'Replace the motherboard first'},
    # ---------------------------------------------------------------- chapter 4
    'Q4.0': {'Reimage Windows to rule out software': 'Reimage Windows to rule out a software cause first'},
    'Q4.2': {'Yes if MDM is installed': 'Yes, if MDM is installed on the phone'},
    'Q4.4': {'Rebuild the print server': 'Rebuild the print server for the floor'},
    'Q4.6': {'Printer panel → app → spooler → port': 'Printer panel → app → spooler → port → cable'},
    'Q4.7': {'The vendor needs the code to ship the order': 'The vendor needs the codes before it can ship any order'},
    'Q4.8': {'Remove the work profile and re-add it': 'Remove the work profile and then re-add it'},
    'Q4.9': {'You closed the ticket without a note': 'You closed the ticket quickly, without writing a note'},
    # ---------------------------------------------------------------- chapter 5
    'Q5.6': {'Yes, if the address is in the APIPA range': 'Yes, if the address it shows is in the APIPA range'},
    'Q5.7': {'Yes. It can replace WPA2/WPA3 encryption': 'Yes. A hidden SSID can replace WPA2/WPA3 encryption'},
    'Q5.9': {'Reimage first, then test the network': 'Reimage first, then test the network and the app'},
    # ---------------------------------------------------------------- chapter 6
    'Q6.0': {'A physical server in a data centre': 'A physical server rack-mounted in a data centre'},
    'Q6.1': {'Reinstall Windows on each guest': 'Reinstall Windows on each of the guests'},
    'Q6.2': {'The hypervisor cluster': 'The vendor’s hypervisor cluster'},
    'Q6.3': {'Reimage the first laptop': 'Reimage the first laptop that reported it'},
    'Q6.4': {'The vendor datacenter': 'The vendor’s datacenter hardware'},
    'Q6.5': {'A full off-site copy of the guest disk': 'A full off-site copy of the guest disk, kept for years'},
    'Q6.7': {'The Windows Setup team for the guest': 'The Windows Setup team, to reinstall the guest OS'},
    'Q6.8': {'Delete every snapshot on the host': 'Delete every snapshot on the host to free space'},
    # ---------------------------------------------------------------- chapter 7
    'Q7.0': {'Flush DNS and close the ticket': 'Flush DNS and then close the ticket'},
    'Q7.1': {'Yes, if the ticket is marked urgent': 'Yes, if the ticket is marked urgent by the user'},
    'Q7.3': {'Task Manager looks calm again': 'Task Manager looks calm again on the PC'},
    'Q7.4': {'Print path': 'Print path / spooler'},
    'Q7.7': {'Look into it': 'Please look into it later'},
    'Q7.9': {'Always list disk': 'You forgot to run list disk'},
    # ---------------------------------------------------------------- chapter 8
    'Q8.2': {'Clean keeps apps; in-place wipes the volume': 'Clean keeps apps and files; in-place wipes the whole OS volume'},
    'Q8.5': {'DNS answers slowly but correctly': 'DNS answers slowly, but every name still resolves'},
    'Q8.6': {'Run diskpart clean on the drive': 'Run diskpart clean on the drive to reset it'},
    'Q8.8': {'Reset the PC, then collect About': 'Reset the PC, then collect About, Update and service states'},
    'Q8.9': {'You deleted a snapshot on someone else’s host': 'You deleted a snapshot on someone else’s host to save space'},
    # ---------------------------------------------------------------- chapter 9
    'Q9.0': {'Which partitions diskpart lists': 'Which partitions diskpart lists on Disk 0'},
    'Q9.1': {'A shortcut that needs no note': 'A shortcut that needs no note in the ticket'},
    'Q9.3': {'Yes, to skip the FileVault prompt': 'Yes, to skip the FileVault prompt at login'},
    'Q9.5': {'Break/fix — network card': 'Break/fix — the network card'},
    # ---------------------------------------------------------------- chapter 10
    'Q10.0': {'Turn it off for games': 'Turn it off for games only'},
    'Q10.4': {'Investigate alone as the incident responder': 'Investigate it alone, acting as the incident responder'},
    'Q10.5': {'In team chat for the hand-off': 'In team chat for the hand-off to the next technician'},
    'Q10.7': {'Tell the user off so it does not happen again': 'Tell the user off firmly, so it does not happen again'},
    'Q10.8': {'Lecture only': 'Lecture the user only, no reset'},
    # ---------------------------------------------------------------- chapter 11
    'Q11.3': {'Order a replacement NIC from the vendor': 'Order a replacement NIC from the vendor right away'},
    'Q11.5': {'Only the user’s verbal OK': 'Only the user’s verbal OK on the phone'},
    'Q11.7': {'Yes. A clean image is always fastest': 'Yes. A clean image is always the fastest route back'},
    # ---------------------------------------------------------------- chapter 12
    'Q12.3': {'By disabling the firewall instead': 'By disabling the firewall for them instead, just this once'},
    'Q12.4': {'RAID is the off-site copy; snapshots are local': 'RAID is the off-site copy; snapshots are the local copy'},
    'Q12.6': {'After you wipe': 'After you wipe the old disk'},
    'Q12.8': {'Open the PSU to check the hardware': 'Open the PSU to check the laptop’s hardware first'},
    'Q12.9': {'Domains mixed in one note with no label': 'Domains mixed together in one note with no label'},
    # ---------------------------------------------------------------- chapter 13
    'Q13.3': {'A reboot substitute for thinking': 'A reboot substitute for thinking it through'},
    'Q13.4': {'gui-accounts and gui-update': 'gui-accounts and gui-update only'},
    'Q13.6': {'Hyper-V delete-all, snapshots, vSwitch': 'Hyper-V delete-all, snapshots, vSwitch, uplinks'},
    'Q13.8': {'The DHCP server’s full scope': 'The DHCP server’s full scope and leases'},
    'Q13.9': {'You left the firewall off to save time': 'You left the firewall off to save time in the lab'},
    # pass-14 items (Pending SME review)
    'Q12.11': {'A new asset tag is issued, because the device has a new home': 'A new asset tag is issued, because the device now has a new home'},
    'Q13.11': {'Get-DnsClientCache': 'Get-DnsClientServerAddress'},
    # ---------------------------------------------------------------- NETOPS
    'NQ1.0': {'Transport (TCP ports)': 'Transport layer (TCP and UDP port numbers)'},
    'NQ1.6': {'UDP guarantees ordered delivery': 'UDP guarantees ordered delivery of every reply packet'},
    'NQ2.0': {'Sends it to the default gateway': 'Sends it to the default gateway, which knows every MAC'},
    'NQ2.1': {'A duplex mismatch on one port': 'A duplex mismatch on one of the access ports'},
    'NQ2.3': {'The spanning-tree root bridge': 'The spanning-tree root bridge priority'},
    'NQ2.6': {'Cat5e with a repeater': 'Cat5e with a repeater midway'},
    'NQ3.2': {'Only private addresses': 'Only destinations in the private RFC 1918 ranges'},
    'NQ3.3': {'A screenshot of the speed test site': 'A screenshot of one speed test from your own laptop'},
    'NQ4.1': {'A static route on each client': 'A static route to the DHCP server on each client'},
    'NQ4.4': {'A wrong subnet mask on the server': 'A wrong subnet mask configured on the web server'},
    'NQ4.6': {'Inbound port forwarding': 'Inbound port forwarding (DNAT)'},
    'NQ4.7': {'It is permitted, because specific rules win': 'It is permitted, because the more specific rule always wins over a deny'},
    'NQ5.2': {'So SNMP does not need a password': 'So SNMP no longer needs a community string or password'},
    'NQ5.4': {'Enable Telnet with a longer password': 'Enable Telnet, but with a longer and more complex password'},
    'NQ5.5': {'It makes the devices boot faster': 'It makes the devices boot faster after a power cut'},
    'NQ5.6': {'Putting guests on the staff VLAN with a different SSID name': 'Putting guests on the staff VLAN, but with a different SSID name'},
    'NQ6.0': {'Each affected user’s PC in turn': 'Each affected user’s PC in turn, one by one'},
    'NQ6.1': {'The data-centre firewall': 'The data-centre firewall rules'},
    'NQ6.2': {'Wait for the problem to clear by itself': 'Wait for the problem to clear by itself before changing anything',
              'Reboot the core to rule everything out': 'Reboot the core switches and firewalls to rule everything out at once'},
    'NQ6.3': {'To avoid writing status updates': 'To avoid writing status updates while the team is busy fixing'},
    'NQ6.6': {'Wait a week and see if anyone complains': 'Wait a week and see whether any of the affected users complain'},
    'NQ6.7': {'Nothing, if service is restored': 'Nothing more, as long as the service has been restored'},
    'NQ9.2': {'show vlan brief': 'show interfaces status'},
    'NQ9.3': {'A routed access port per VLAN': 'A separate routed access port for each VLAN'},
    'NQ9.4': {'ip route 203.0.113.1 0.0.0.0': 'ip route 203.0.113.1 255.255.255.255 0.0.0.0'},
    'NQ9.5': {'Changing the VLAN': 'Changing the access VLAN number'},
    'NQ9.6': {'show running-config': 'show running-config | section interface'},
    'NQ9.7': {'An ARP entry for the router itself': 'An ARP entry for the router’s own subinterface address'},
}


def apply(bank_id, options, correct):
    """Return (options, correct) with this item's rewrites applied in place (order unchanged)."""
    rw = REWRITE.get(bank_id)
    if not rw:
        return options, correct
    return [rw.get(o, o) for o in options], rw.get(correct, correct)
