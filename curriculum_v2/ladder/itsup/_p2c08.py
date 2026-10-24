"""Option B pass 2 — ITSUP chapter 8 bespoke ladders (formerly same_as). Pending SME review."""
from curriculum_v2.ladder.itsup._p2 import B
from curriculum_v2.ladder.schema import order, reveal, sort

INST, CLEAN, UPD, REBOOT = 'MC-IT8-INSTALL-FIRST', 'MC-IT8-CLEAN-VS-INPLACE', 'MC-IT8-UPDATE-IGNORED', 'MC-IT8-REBOOT-CLEARS'
DESTR, TOOL, FWOK, DHCPS = 'MC-R3-IT8-DESTRUCTIVE-FIRST', 'MC-C-IT8-REPAIR-TOOL', 'MC-IT8-FIREWALL-OFF-OK', 'MC-IT8-DHCP-SERVICE-SYMPTOM'
CHG = 'MC-R3-IT8-CHANGE-BEFORE-ACCOUNT'
LUP = ('gui-update', 'Read the update state and history before deciding on any repair or install.')
LACC = ('gui-accounts', 'Note who is signed in before you change anything.')
LSVC = ('gui-services', 'Record the state of the three named services before deciding the next window.')


def _s(n, t):
    return f'Course lesson 8.{n} “{t}” (the original section), re-explained'


S1, S2, S4 = _s(1, 'Installing Windows'), _s(2, 'Configuring Windows'), _s(4, 'Failed Update Capstone')
SECS = {}


def _add(label, sid, *a):
    SECS[(label, sid)] = B(label, sid, *a)


_add('8.1', '1-choose-with-evidence', '1. Choose with evidence', 'IT-8.1', S1, [
    ('The OS boots but a feature update failed. Which install?', 'In-place upgrade', 'Clean install now', 'Neither, replace RAM',
     'In-place fits a booting OS with a broken component store or failed feature update.', CLEAN, INST),
    ('When is a clean install justified?', 'Volume is trash, backup OK', 'Whenever it is quicker', 'After any failed update at all',
     'Clean only when the volume is beyond repair and the backup is confirmed.', CLEAN, DESTR),
    ('In the house story, what is redecorating while living there?', 'In-place upgrade', 'Clean install', 'A POST memory test',
     'You keep the furniture while fixing the walls, like keeping apps and files.', CLEAN, CLEAN),
    ('In the decision picture, POST memory fails. Where do you go?', 'Chapter 2.5', 'setup.exe', 'In-place upgrade',
     'A POST memory failure is hardware; no installer can fix it.', INST, INST),
    ('Which fact must be confirmed before a clean install?', 'The backup', 'The wallpaper', 'The user’s phone',
     'A clean install wipes the volume; the backup must exist first.', DESTR, DESTR),
],
    (['Pick the install type from the evidence.', 'Does Windows still boot?', 'Is the problem a failed update or broken system files?', 'Then use an in-place upgrade.',
      'Is the disk volume beyond repair?', 'Is the backup confirmed?', 'Then a clean install is allowed.', 'Memory errors at POST are hardware.', 'No installer fixes those.'],
     'Boots with broken updates: in-place. Trashed volume with backup: clean. POST failure: hardware first.'),
    ('If the walls of your house are cracked, you repair them while living there. If the house is condemned, you move everything out '
     'first and rebuild. If the front door will not open at all, you call a locksmith before any builder.',
     [('Repairing walls while living there', 'In-place upgrade'), ('Moving out and rebuilding', 'Clean install after backup'),
      ('Condemned house', 'Volume beyond repair'), ('Door will not open', 'POST failure: hardware')],
     'A house can be partly rebuilt; Windows setup is all or nothing per volume, so pick the right one before starting.'),
    ('flow', 'Choosing an install', ['POST OK?', 'OS boots?', 'Store or update broken', 'In-place upgrade']),
     'If POST fails, stop at the first box and go to Chapter 2.5. If the volume is trash and backup is confirmed, a clean install replaces the last box.',
    'Sort each case, then read the update history in the lab before choosing.',
    sort('Which path?', {'In-place upgrade': ['Boots, feature update failed', 'Boots, component store broken'],
                         'Clean install': ['Volume trash, backup confirmed'], 'Hardware first': ['POST memory beep codes']}, 'Evidence picks the path.'), LUP)

_add('8.1', 'clean-versus-in-place', 'Clean versus in-place', 'IT-8.1', S1, [
    ('What does a clean install remove?', 'The OS volume', 'Only temp files', 'Nothing at all',
     'Clean wipes the OS volume; in-place tries to keep apps and files.', CLEAN, CLEAN),
    ('Is an in-place upgrade a change?', 'Yes, both are changes', 'No, it is just a repair', 'No, it is reversible',
     'Both install types are changes and need a plan and an undo.', CLEAN, CLEAN),
    ('In the phone story, what is a factory reset?', 'A clean install', 'An in-place upgrade', 'A POST test',
     'A factory reset wipes everything, like a clean install.', CLEAN, CLEAN),
    ('In the comparison picture, what does in-place keep?', 'Apps and files', 'Only the wallpaper', 'Nothing at all',
     'In-place tries to keep apps, settings and files.', CLEAN, CLEAN),
    ('The PC never leaves POST. Which install is step one?', 'Neither of them', 'Clean install', 'In-place upgrade',
     'Neither is step one on a box that never leaves POST.', INST, INST),
],
    (['There are two ways to reinstall Windows.', 'A clean install wipes the OS drive.', 'An in-place upgrade tries to keep apps and files.',
      'Both are changes.', 'Both need a plan.', 'Neither is the first step on a PC stuck at POST.', 'That PC has a hardware problem.'],
     'Clean wipes, in-place keeps, and both wait until the hardware passes POST.'),
    ('A phone can get a system update that keeps your photos and apps, or a factory reset that wipes it back to new. Both change the '
     'phone. Neither helps if the phone will not even switch on.',
     [('System update that keeps photos', 'In-place upgrade'), ('Factory reset', 'Clean install'), ('Photos and apps', 'User files and applications'),
      ('Phone will not switch on', 'PC stuck at POST')],
     'A phone update is routine; an in-place Windows upgrade is a bigger, slower change that still needs backup and a plan.'),
    ('two', 'Clean versus in-place', (('Clean install', ['Wipes the OS volume', 'Needs confirmed backup', 'Volume is trash']),
                                      ('In-place upgrade', ['Keeps apps and files', 'Still a change', 'OS boots, store broken']))),
     'Both columns are changes. Neither column applies before POST passes, because no installer reaches a PC that cannot start.',
    'Sort each fact, then read the update state in the lab.',
    sort('Clean or in-place?', {'Clean install': ['Wipes the OS volume', 'Needs a confirmed backup first'],
                                'In-place upgrade': ['Tries to keep apps and files', 'Fixes a broken component store']}, 'Both are changes.'), LUP)

_add('8.2', 'baseline-is-a-description', 'Baseline is a description', 'IT-8.2', S2, [
    ('What belongs in a baseline?', 'Who is signed in', 'A list of tweaks', 'The user’s mood',
     'A baseline describes the box: user, update state, address.', CHG, CHG),
    ('When do you collect the baseline?', 'Before you tune', 'After you tune', 'Only if it fails',
     'Describe the box first so any change can be compared to it.', REBOOT, REBOOT),
    ('In the doctor story, what is the baseline?', 'Readings before treatment', 'The prescription', 'The bill paid afterwards at the desk',
     'Readings before treatment let you see what changed.', REBOOT, REBOOT),
    ('In the picture, which three views describe the PC?', 'Update, accounts, ethernet', 'BIOS, CPU and RAM size', 'Mail, Teams and the Word apps',
     'gui-update, gui-accounts and gui-ethernet are three views of one PC.', CHG, CHG),
    ('The box has 169.254. Part of the baseline?', 'Yes, a real address fact', 'No, it is irrelevant', 'No, tune the settings first',
     'Whether the box has a real address is a baseline fact.', DHCPS, DHCPS),
],
    (['A baseline describes the PC as it is now.', 'Who is signed in?', 'Is Windows Update pending or failed?', 'Does it have a real address?',
      'Collect these before you tune anything.', 'Three lab screens show the same PC.', 'Update, accounts and Ethernet.'],
     'Describe the box first; tune only after you have the description.'),
    ('A doctor takes your temperature, pulse and weight before giving any medicine. Later readings mean nothing without the first '
     'ones. The doctor writes them down, not “seems fine”.',
     [('Temperature, pulse, weight', 'Signed-in user, update state, address'), ('Before medicine', 'Before tuning'),
      ('Later readings', 'State after a change'), ('“Seems fine”', 'An adjective instead of a fact')],
     'Your body changes slowly; a PC can change in one reboot, so take the baseline right before you act.'),
    ('flow', 'Collect the baseline', ['gui-accounts: who', 'gui-update: state', 'gui-ethernet: address', 'Write it down', 'Then tune']),
     'The first three boxes are three views of one PC. Tuning is the last box and only starts once the description is written.',
    'Order the baseline, then read who is signed in using the accounts lab.',
    order('Baseline order', ['Who is signed in', 'Update pending or failed', 'Real address or not', 'Write the description', 'Only then tune'],
          'A description has values, not adjectives.'), LACC)

_add('8.2', 'what-pending-update-does-to-a-ticket', 'What pending update does to a ticket', 'IT-8.2', S2, [
    ('What can a pending feature update explain?', 'Random reboots', 'MEM beep codes', 'A swollen battery',
     'A pending update can reboot a PC; it cannot cause POST memory beeps.', UPD, UPD),
    ('Update failed with a code. What goes in the ticket?', 'The exact code', '“Update broke”', 'A guess at the cause',
     'Copy the code verbatim; it is evidence.', REBOOT, REBOOT),
    ('In the delivery story, what is the parcel slip number?', 'The error code', 'The reboot', 'The update itself',
     'The slip number lets anyone trace the parcel, like an error code.', REBOOT, REBOOT),
    ('In the picture, which arrow is wrong?', 'Pending update → MEM beeps', 'Pending update → reboots', 'Failed update → copy the code',
     'A pending update does not cause memory beeps.', UPD, UPD),
    ('Why copy the code verbatim?', 'So others can look it up', 'To fill the ticket', 'Codes are only decoration',
     'An exact code can be searched and compared.', REBOOT, REBOOT),
],
    (['A pending feature update can restart the PC at odd times.', 'So it can explain random reboots.', 'It cannot explain memory beeps.',
      'Those come from POST.', 'If an update failed, it shows a code.', 'Copy that code into the ticket exactly.'],
     'Link reboots to pending updates, never beeps, and copy failure codes word for word.'),
    ('A delivery driver may knock at odd hours, which explains a surprise at the door. It does not explain a burst pipe. If a parcel '
     'goes missing, the slip number is what lets the depot find it.',
     [('Driver knocking at odd hours', 'Pending update rebooting'), ('Burst pipe', 'POST memory beeps'), ('Slip number', 'Update error code'),
      ('Depot', 'Microsoft docs and the next technician')],
     'A driver can be called; an update cannot explain itself, so the code is the only reliable evidence you have.'),
    ('two', 'What a pending update explains', (('Explains', ['Random reboots', 'Restart prompts']), ('Does not explain', ['MEM beep codes', 'No POST at all']))),
     'If the symptom is in the right column, look elsewhere. If an update failed, its code goes in the ticket exactly.',
    'Reveal the answer after you write the ticket line.',
    reveal('Update history shows “2024-09 Cumulative Update – failed (0x800f0922)” and the user reports random restarts. Ticket line?',
           '“Update failed 0x800f0922 (verbatim); pending restart state noted; random restarts consistent with pending update. No POST beeps.”'), LUP)

_add('8.4', 'failed-update-capstone', 'Failed update capstone', 'IT-8.3', S4, [
    ('What does the capstone collect?', 'About, error, three services', 'Only a screenshot or two', 'A clean install log from setup',
     'About, the update error, three service states and the next window.', REBOOT, DESTR),
    ('Is a clean install allowed here?', 'No', 'Yes', 'Only on Fridays',
     'The OS still logs in; no clean install is allowed.', DESTR, DESTR),
    ('In the car story, what is the next service slot?', 'The next window', 'The error code', 'The engine block',
     'Deciding retry, in-place or escalate is booking the next slot.', REBOOT, REBOOT),
    ('In the picture, which option is NOT a next window?', 'Turn Defender off', 'Retry the update', 'Escalate to the owner',
     'Defender stays on; the windows are retry, in-place or escalate.', FWOK, FWOK),
    ('The OS still logs in. What does that rule out?', 'A clean install', 'Reading About', 'Collecting errors',
     'A working login means no clean install; collect evidence instead.', DESTR, DESTR),
],
    (['The PC still logs in.', 'Collect About.', 'Collect the update error.', 'Check three services.', 'Choose the next window.',
      'Retry, in-place, or escalate.', 'No clean install.', 'No turning Defender off.'],
     'Collect About, the error and three services, then pick retry, in-place or escalate.'),
    ('A car fails its service but still drives. The garage writes the model, the fault code and three readings, then books one of three '
     'slots: try again, a bigger repair, or send it to the dealer. Nobody scraps it, and nobody pulls the airbag fuse.',
     [('Model', 'About'), ('Fault code', 'Update error'), ('Three readings', 'Three service states'), ('Three slots', 'Retry, in-place, escalate'),
      ('Scrapping the car', 'Clean install'), ('Pulling the airbag fuse', 'Turning Defender off')],
     'A car can be test-driven between slots; an update retry may need a reboot that the user must agree to first.'),
    ('flow', 'Evidence before the decision', ['Sign-in works', 'Model and build', 'Exact failure code', 'Service states', 'Pick a path']),
     'Read the chart from left to right. The final box gives three possible paths: try again, upgrade over the top, or hand it up. Wiping the machine and switching protection off are never paths.',
    'Order the capstone, then record three service states in the services lab.',
    order('Capstone steps', ['Confirm it still logs in', 'Collect About', 'Copy the update error', 'Record three service states', 'Choose the next window'],
          'No clean install, no Defender off.'), LSVC)
