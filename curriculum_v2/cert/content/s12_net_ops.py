"""Network+ 2.4 (physical installations) and 3.3 (disaster recovery) — NETOPS 6.3."""
from ..authoring import cfu, figure, match, multi, order, scenario, single, sme_note, worked

_FIG = figure(
    'fig-c-dr', 'Recovery metrics on a timeline',
    ['Last good\nbackup', '← RPO: data\nyou can lose', 'Disaster', 'RTO: time to\nrestore →', 'Service\nrestored'],
    'Five boxes along a timeline from left to right. The last good backup is followed by the recovery point objective, the '
    'maximum amount of data, measured in time, the business can afford to lose. Then the disaster. Then the recovery time '
    'objective, the maximum time allowed to restore the service. Then service is restored. A one-hour RPO needs backups or '
    'replication at least hourly; a one-hour RTO needs a recovery method that can be completed in an hour, such as a warm or '
    'hot site.',
    'RPO looks backwards from the disaster (data loss); RTO looks forwards (downtime).', cols=5)

HTML = f'''
<h4>Physical installations (Network+ 2.4)</h4>
<ul>
<li><strong>MDF</strong> (main distribution frame) — where the provider lines, core switching and servers are;
<strong>IDF</strong> (intermediate distribution frame) — a wiring closet serving one floor or area, linked back to the MDF.</li>
<li><strong>Racks</strong> are 19 inches wide and measured in rack units (1U = 1.75 in). Match the equipment’s
<strong>port-side exhaust or intake</strong> airflow to the room’s hot-aisle / cold-aisle layout, or devices recirculate hot air.</li>
<li><strong>Cabling</strong> — copper terminates on a <strong>patch panel</strong>, fibre on a <strong>fibre distribution panel</strong>;
racks and cabinets should be <strong>lockable</strong>.</li>
<li><strong>Power</strong> — a <strong>UPS</strong> bridges outages and conditions power; a <strong>PDU</strong> distributes it to the
equipment in a rack. Check the <strong>power load</strong> against the UPS and circuit rating, and the <strong>voltage</strong>
the equipment expects.</li>
<li><strong>Environment</strong> — <strong>temperature</strong> (ASHRAE’s recommended inlet range is 18–27 °C),
<strong>humidity</strong> (too dry risks static, too damp risks condensation) and <strong>fire suppression</strong> suited to
electronics (clean-agent systems rather than water where possible).</li>
</ul>
<h4>Disaster recovery (Network+ 3.3)</h4>
<p>NIST SP 800-34 defines the planning terms. <strong>RPO</strong> (recovery point objective) — how much data, in time,
can be lost. <strong>RTO</strong> (recovery time objective) — how long the service may be down. <strong>MTTR</strong>
(mean time to repair) — average time to fix a failed component. <strong>MTBF</strong> (mean time between failures) — average
operating time between failures of a repairable component.</p>
{_FIG}
<ul>
<li><strong>Sites:</strong> a <strong>cold site</strong> has space and power only (slowest, cheapest); a <strong>warm
site</strong> has hardware and connectivity but needs current data restored; a <strong>hot site</strong> runs in parallel with
near-current data (fastest, most expensive).</li>
<li><strong>High-availability approaches:</strong> <strong>active-active</strong> — both systems carry load, and either can
take all of it; <strong>active-passive</strong> — a standby takes over when the active system fails.</li>
<li><strong>Testing:</strong> <strong>tabletop exercises</strong> walk the team through a scenario on paper; <strong>validation
tests</strong> actually fail over or restore to prove the plan works.</li>
</ul>
{worked('choosing a recovery site', '''<ol>
<li>The order system’s business owner sets RPO = 15 minutes and RTO = 1 hour.</li>
<li>Nightly backups give a 24-hour RPO — not enough. Database replication to a second site is needed.</li>
<li>A cold site could take days to equip — fails the RTO. A warm site with replicated data and pre-built servers can meet one hour.</li>
<li>Prove it with a validation test (planned failover) twice a year, and a tabletop exercise for the people involved.</li></ol>''')}
{scenario('the hot closet', '''<p>An IDF switch reboots every afternoon in summer. The closet has no ventilation, the switch’s fans blow into the
back of a shelf, and the UPS display shows 92 % load. You log the temperature, re-mount the switch so its exhaust matches the
airflow, request ventilation for the closet, and move non-essential load off the UPS. The reboots stop; the change and the
readings go in the documentation.</p>''')}
{cfu(('What is the difference between RPO and RTO?', 'RPO is the acceptable data loss (time since the last good copy); RTO is the acceptable downtime.'),
     ('Which site type has hardware and network but needs current data restored?', 'A warm site.'),
     ('What does a PDU do that a UPS does not?', 'It distributes power to the equipment in a rack; the UPS provides battery backup.'))}
'''

SUPPLEMENTS = [{
    'course': 'NETOPS', 'chapter': 6, 'lesson': 3, 'id': 'cert-phys-dr',
    'title': 'Physical installations and disaster recovery',
    'cert': ['N:2.4', 'N:3.3'],
    'html': sme_note('Physical installation factors and disaster-recovery concepts (Network+ 2.4 and 3.3).') + HTML,
    'sources': ['nist-80034r1', 'ashrae-tc99', 'eia-310'],
}]

GLOSSARY = [
    ('MDF / IDF', 'Main distribution frame (central wiring and core equipment) and intermediate distribution frame (a floor or area wiring closet).'),
    ('PDU', 'Power distribution unit: distributes power to the devices in a rack.'),
    ('RPO', 'Recovery point objective: the maximum acceptable data loss, measured in time.'),
    ('RTO', 'Recovery time objective: the maximum acceptable time to restore a service.'),
    ('MTBF', 'Mean time between failures: average operating time between failures of a repairable item.'),
    ('Warm site', 'Recovery site with hardware and connectivity in place but data that must be restored.'),
    ('Tabletop exercise', 'A discussion-based walk-through of a disaster scenario, without touching systems.'),
]

ITEMS = [
    match('N:3.3', 'NO-6.3', 1, 'Match each disaster-recovery term to its definition.',
          [('RPO', 'Maximum acceptable data loss, in time'), ('RTO', 'Maximum acceptable downtime'),
           ('MTTR', 'Average time to repair a failed component'), ('MTBF', 'Average operating time between failures')],
          'NIST SP 800-34 terms and the reliability metrics named in Network+ 3.3.',
          decoys=['Time to live']),
    single('N:3.3', 'NO-6.3', 2, 'A business needs a recovery site that already has hardware and connectivity, but can accept a few hours to restore current data. Which fits?',
           'A warm site',
           ['A hot site', 'A cold site', 'An active-active cluster'],
           'Warm sites have equipment ready but need data restored; hot sites run with current data; cold sites have space and power only.'),
    single('N:3.3', 'NO-6.3', 3, 'The DR team wants to prove the plan works by actually failing the database over to the second site. What type of test is this?',
           'A validation test',
           ['A tabletop exercise', 'A walk-through review', 'A vulnerability scan'],
           'Validation tests exercise the real failover; tabletop exercises are discussion only.'),
    multi('N:3.3', 'NO-6.3', 4, 'Two firewalls both pass traffic, and if one fails the other carries the full load. Which TWO statements are true? (Choose two.)',
          ['This is an active-active design', 'Each firewall must be sized for the full load'],
          ['This is an active-passive design', 'It needs a cold site to work', 'It sets the organisation’s RPO'],
          'Active-active shares load; each unit must handle everything when its partner fails.'),
    single('N:2.4', 'NO-6.3', 1, 'A switch in a cold-aisle/hot-aisle rack overheats although the room is cool. Its fans blow front to back, but its ports face the hot aisle. What is the problem?',
           'Its airflow does not match the aisle layout',
           ['The rack is the wrong width', 'The PDU is overloaded', 'The fibre distribution panel door is unlocked'],
           'Port-side intake/exhaust must match the aisles, or the device draws in hot air.'),
    match('N:2.4', 'NO-6.3', 2, 'Match each item to its purpose in a wiring closet.',
          [('UPS', 'Battery backup and power conditioning'), ('PDU', 'Distributes power to rack equipment'),
           ('Patch panel', 'Terminates copper horizontal cabling'), ('Fibre distribution panel', 'Terminates and protects fibre runs')],
          'Power and cabling components named in Network+ 2.4.',
          decoys=['Network tap']),
    single('N:2.4', 'NO-6.3', 3, 'A wiring closet serves the third floor and connects back to the main equipment room. What is it called?',
           'An intermediate distribution frame (IDF)',
           ['A main distribution frame (MDF) for the building', 'A screened subnet', 'A demarcation point'],
           'IDFs serve floors or areas and link to the MDF.'),
    single('N:2.4', 'NO-6.3', 4, 'Which environmental control is most appropriate for a server room full of powered electronics?',
           'A clean-agent fire suppression system',
           ['A standard wet-pipe sprinkler only', 'Portable water extinguishers only', 'Higher humidity to stop static'],
           'Clean-agent systems suppress fire without water damage to electronics.'),
]
