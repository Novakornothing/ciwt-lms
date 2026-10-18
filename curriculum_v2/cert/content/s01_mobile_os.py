"""A+ Core 2 3.2 and 3.3 — mobile OS, application and mobile-security troubleshooting (ITSUP 4.2)."""
from ..authoring import cfu, figure, multi, order, scenario, single, sme_note, worked, match

_FIG = figure(
    'fig-c-mobile-app', 'Mobile app and OS fault isolation',
    ['Scope it\none app or all?', 'Close and\nreopen the app', 'Restart\nthe device', 'Update app\nand OS',
     'Check storage,\npermissions, network', 'Clear cache / reinstall\n(after backup)'],
    'Six boxes in order. First, scope the fault: does it affect one app, or every app and the operating system? '
    'Then close and reopen the app, restart the device, update the app and the OS, check free storage, app '
    'permissions and the network, and only then clear the app cache or delete and reinstall it, after confirming '
    'that its data is backed up or synced, because removing an app can delete data stored only on the device.',
    'Least-destructive first: every step to the left keeps the user’s data; the last box can lose local app data.', cols=3)

HTML = f'''
<p>Mobile tickets look different from desktop tickets, but the method is the same: scope the fault, change one thing at a
time, and do the steps that cannot lose data first. Both Apple and Google publish the same basic order for an app
that crashes, will not open or stops responding: <strong>close and reopen it, restart the device, update the app and the
operating system, and only then delete and reinstall it</strong>, because deleting an app can remove data stored only in
that app. Android adds two intermediate steps in <em>Settings &gt; Apps</em>: <strong>Force stop</strong> and
<strong>clear cache</strong> (clearing <em>storage/data</em> as well resets the app, so it is a later step).</p>
{_FIG}
<h4>Symptom → first checks</h4>
<table class="ref-table"><thead><tr><th scope="col">Symptom</th><th scope="col">Check first</th><th scope="col">Why</th></tr></thead><tbody>
<tr><td>App fails to launch, or crashes</td><td>Close and reopen; restart; update the app</td><td>Clears a hung process; most crash fixes ship as app updates.</td></tr>
<tr><td>App fails to install or update</td><td>Free storage; OS version meets the app’s minimum; store account signed in; device not blocked by MDM policy</td><td>Installers need space and a supported OS; managed devices may only allow approved apps.</td></tr>
<tr><td>OS fails to update</td><td>Battery charge or charger connected, free storage, stable Wi-Fi, device still supported</td><td>Updates check power and space before installing; older models stop receiving releases.</td></tr>
<tr><td>Poor battery life, device warm</td><td>Battery usage by app; background activity; battery health</td><td>A single runaway app or a worn battery are the usual causes.</td></tr>
<tr><td>Random reboots</td><td>Recent update or new app; battery health; overheating; storage nearly full</td><td>Look for a pattern before resetting anything.</td></tr>
<tr><td>Bluetooth, Wi-Fi or NFC not working</td><td>Toggle the radio, airplane mode off, forget and re-pair or rejoin; then reset network settings</td><td>Reset network settings clears saved Wi-Fi networks and pairings, so it is not the first step.</td></tr>
<tr><td>Screen does not autorotate</td><td>Rotation lock (iPhone Control Center) or Auto-rotate (Android quick settings); some apps support one orientation only</td><td>Almost always a setting, not a sensor fault.</td></tr>
</tbody></table>
<h4>When the symptom is a security symptom</h4>
<p>Some mobile symptoms point at compromise rather than a bug: <strong>high network traffic</strong> or a <strong>data-usage limit
notification</strong> the user cannot explain, <strong>degraded response time</strong>, a <strong>high number of ads</strong> or
pop-ups outside any app, <strong>fake security warnings</strong> that push the user to install something, <strong>unexpected
application behaviour</strong>, limited or no connectivity after installing something, and <strong>leaked personal files or
data</strong> (contacts receiving messages the user did not send). NIST SP 800-124 Rev. 2 lists the root causes to look for:
apps installed from <strong>unofficial app stores</strong> (sideloading), <strong>developer mode</strong> or USB debugging left on,
<strong>root access or a jailbreak</strong> (which removes the operating system’s app sandbox and update protections), and
<strong>malicious or spoofed apps</strong> that imitate a real brand.</p>
<p>The response order matters. Contain first (airplane mode or disconnect from Wi-Fi, and report it if the device is a
managed corporate device), then identify (recently installed apps, apps with device-administrator rights or VPN
and device-management profiles you do not recognise), then remove the cause and verify. Change account passwords
<em>from a different, clean device</em>, because a keylogger on the phone would capture the new password. A rooted or
jailbroken device cannot be trusted again until it is restored to the vendor’s firmware; on a managed device, the MDM
compliance policy normally flags it and blocks corporate apps until that happens.</p>
{worked('Android app crashes after an update', '''<ol>
<li><strong>Scope:</strong> only the expense app crashes; other apps and the camera work. One-app fault, not the OS.</li>
<li><strong>Least destructive:</strong> force stop, reopen — still crashes. Restart the phone — still crashes.</li>
<li><strong>Update:</strong> Play Store shows a newer build of the app; install it — still crashes at launch.</li>
<li><strong>Cache:</strong> Settings &gt; Apps &gt; Expense &gt; Storage &amp; cache &gt; Clear cache. The app opens.</li>
<li><strong>Verify and document:</strong> user submits a test claim; ticket notes the build number and that clearing
storage/data was not needed, so no local drafts were lost.</li></ol>''')}
{scenario('the phone with too many ads', '''<p>A sales rep says her personal Android phone “shows adverts on the home screen” and her monthly data warning
arrived two weeks early. Settings shows a torch app installed from a link in a text message last week, with
permission to display over other apps. That fits three Core 2 3.3 symptoms at once (high number of ads, high data
usage, an app from an unofficial source). You put the phone in airplane mode, remove the app, run a Google Play
Protect scan, check that no unknown device-admin app remains, and advise her to change the passwords she typed
since the install from her laptop. If the symptoms return, back up photos and contacts and factory-reset.</p>''')}
{cfu(('Why is “delete and reinstall the app” late in the order, not early?', 'Deleting an app can delete data stored only on the device; Apple and Google both list it after restart and update.'),
     ('A phone will not rotate the screen in any app. What do you check first?', 'Rotation lock / Auto-rotate in the quick settings — it is almost always a setting.'),
     ('Why change passwords from a different device after a suspected mobile compromise?', 'Malware on the phone (a keylogger or overlay) could capture the new password.'),
     ('Name two root causes of mobile security issues listed in Core 2 3.3.', 'Any two of: unofficial app stores/sideloading, developer mode, root access/jailbreak, malicious or spoofed apps.'))}
'''

SUPPLEMENTS = [{
    'course': 'ITSUP', 'chapter': 4, 'lesson': 2, 'id': 'cert-mobile-os',
    'title': 'Troubleshooting mobile OS, app and mobile-security issues',
    'cert': ['A2:3.2', 'A2:3.3', 'A1:5.4'],
    'html': sme_note('Mobile OS and application troubleshooting, and mobile security symptoms (A+ Core 2 3.2 and 3.3).') + HTML,
    'sources': ['apple-app', 'android-app', 'nist-800124r2'],
}]

GLOSSARY = [
    ('Force stop', 'Android setting that ends an app’s processes completely; less drastic than clearing its storage.'),
    ('Clear cache (mobile app)', 'Removes an app’s temporary files without removing its accounts or saved data; clearing storage/data resets the app.'),
    ('Sideloading', 'Installing an app from outside the platform’s official store; a common route for malicious apps.'),
    ('Jailbreak / root', 'Removing the operating system’s restrictions to gain full control; it also removes sandbox and update protections.'),
    ('Rotation lock', 'Setting that keeps the screen in one orientation (Auto-rotate on Android); the usual cause of “screen will not rotate”.'),
]

ITEMS = [
    single('A2:3.2', 'IT-4.2', 1, 'An iPhone app freezes on its loading screen every time it opens. Other apps work. What should the technician try first?',
           'Close the app completely, then reopen it',
           ['Reset all settings on the iPhone', 'Delete the app and reinstall it from the store', 'Erase the iPhone and restore from backup'],
           'Apple’s order is close and reopen, restart, update, then delete and reinstall; the first step loses nothing.'),
    single('A2:3.2', 'IT-4.2', 2, 'A user cannot install a required app; the store says the item is not compatible. The phone has plenty of free space. What is the most likely cause?',
           'The phone’s OS version is below the app’s minimum',
           ['The phone’s battery health is below 80 percent', 'The cellular data plan has reached its limit', 'Bluetooth is turned on during the install'],
           'Store compatibility messages are about OS version or hardware support, not battery, data plan or radios.'),
    single('A2:3.2', 'IT-4.2', 3, 'No app on a user’s tablet rotates to landscape any more, including the web browser. What is the most likely fix?',
           'Turn off rotation lock in the quick settings',
           ['Replace the tablet’s accelerometer sensor', 'Reinstall each app that will not rotate', 'Update the tablet’s display driver firmware'],
           'A fault in every app at once is almost always the rotation lock / Auto-rotate setting.'),
    order('A2:3.2', 'IT-4.2', 4, 'An Android app keeps crashing. Put these steps in the order Google’s Android Help article gives them.',
          ['Restart the phone', 'Update the app and Android', 'Force stop the app', 'Clear the app’s cache and data',
           'Uninstall the app (data saved in it is erased)'],
          'Android Help: Step 1 restart and update; Step 2 force stop, then clear cache and data; uninstalling erases data saved in the app, so it comes last.'),
    multi('A2:3.3', 'IT-4.2', 1, 'A phone shows a data-usage warning early in the month and pop-up ads on the home screen. Which TWO findings would best explain both symptoms?',
          ['An app installed from a link outside the official store', 'An unknown app with permission to display over other apps'],
          ['Auto-brightness is turned off', 'The phone is set to a 30-second auto-lock', 'Wi-Fi calling is turned on', 'The battery health reads 85 percent'],
          'Sideloaded or overlay-capable apps are the classic cause of ads outside apps and unexplained data use. The other settings do not cause either symptom.'),
    single('A2:3.3', 'IT-4.2', 2, 'An MDM compliance report flags a corporate phone as jailbroken. What is the best next step?',
           'Block corporate access and reset to stock firmware',
           ['Allow access because the phone still passes PIN checks', 'Install a third-party antivirus app and keep using it', 'Turn off developer mode and leave the jailbreak'],
           'A jailbreak removes the OS sandbox and update protections, so the device cannot be trusted until it is restored.'),
    single('A2:3.3', 'IT-4.2', 3, 'After removing a malicious app from a user’s phone, from where should the user change their account passwords?',
           'From a different device that is known to be clean',
           ['From the same phone, as soon as the app is gone', 'From the phone once it has been restarted twice', 'From any public kiosk computer in the building'],
           'If anything else on the phone captures input, a new password typed on it is exposed; use a trusted device.'),
    match('A2:3.3', 'IT-4.2', 4, 'Match each mobile symptom to the most likely root cause.',
          [('Ads appear on the home screen, outside any app', 'Malicious or adware app'),
           ('Banking app refuses to run: “device integrity check failed”', 'Root access or jailbreak'),
           ('Phone accepts commands from a USB-connected PC without prompting', 'Developer mode / USB debugging left on'),
           ('App looks like the real brand but asks for card details at launch', 'Spoofed (fake) app')],
          'Each symptom has one characteristic cause listed in Core 2 3.3; “weak Wi-Fi” is a decoy that causes none of them.',
          decoys=['Weak Wi-Fi signal']),
    single('A1:5.4', 'IT-4.1', 1, 'A phone’s battery lasts half a day and the phone feels warm in a pocket. Battery settings show one navigation app using 60 percent in the background. What should the technician do first?',
           'Restrict or close that app’s background activity',
           ['Replace the battery because it has failed', 'Factory-reset the phone to remove the fault', 'Disable the cellular radio until a fix is found'],
           'Battery usage by app points at one runaway app; fix the cause before replacing hardware or resetting.'),
]
