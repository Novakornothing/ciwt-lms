"""Deep, SME-Grade Windows 10/11 & Linux Boot Process Architecture & Fault Isolation Reference.

Provides comprehensive, 6-stage engineering walkthroughs, symptom-to-stage diagnostic matrices,
WinRE / GRUB2 / systemd recovery playbooks, and full-width annotated SVG architecture diagrams
for:
  - ITSUP 2.2 (Firmware: UEFI, Secure Boot, and Settings)
  - ITSUP 8.1 / CLIENT 1.1 (Clean vs In-Place Windows Installation & Partitioning)
  - ITSUP 8.2 / CLIENT 1.2 (Baseline Configuration & Windows Session Init)
  - ITSUP 8.3 / CLIENT 1.3 (Windows Repair Tools, WinRE & BCD Recovery)
  - ITSUP 9.1 / CLIENT 2.1 (Linux CLI Essentials & UEFI/GRUB2/initramfs/systemd Boot Chain)

Safe for Explanation Ladder (`curriculum_v2/ladder/sections.py`):
- Wrapped in `<article class="novak-boot-deep-dive" ...>...</article>` with `<h4>`/`<h5>` headings
  so `<section class="sublesson">` boundaries and `r0_sha` hashes remain 100% intact.
"""
from __future__ import annotations

import re

_BOOT_ARTICLE_RE = re.compile(
    r'\n*<article\s+class="novak-boot-deep-dive"[^>]*>.*?</article>\n*',
    re.DOTALL | re.IGNORECASE,
)

WIN_BOOT_6STAGE_SVG = (
    '<figure class="novak-boot-svg-figure" style="margin:0.9rem 0">'
    '<svg viewBox="0 0 760 225" width="100%" role="img" '
    'aria-label="Windows 10 and 11 6-Stage UEFI, GPT, BCD, Kernel, and Winlogon Boot Pipeline Diagram" '
    'class="novak-boot-pipeline-svg" style="display:block;height:auto;max-width:100%;background:#0b1120;border:1px solid rgba(56,189,248,0.35);border-radius:10px">'
    '<rect x="0" y="0" width="760" height="30" rx="10" fill="#1e293b"/>'
    '<text x="16" y="19" fill="#f8fafc" font-family="system-ui,-apple-system,sans-serif" font-size="11" font-weight="700">'
    'WINDOWS 10/11 6-STAGE UEFI/GPT BOOT PIPELINE &amp; FAULT ISOLATION MAP (220-1201 / 220-1202)</text>'
    '<text x="744" y="19" text-anchor="end" fill="#38bdf8" font-family="ui-monospace,Consolas,monospace" font-size="9" font-weight="700">6-STAGE CHAIN</text>'
    # Stage 1
    '<g transform="translate(12,42)">'
    '<rect width="114" height="145" rx="7" fill="#0f172a" stroke="#38bdf8" stroke-width="1.5"/>'
    '<rect x="6" y="6" width="102" height="18" rx="4" fill="#38bdf8" fill-opacity="0.18"/>'
    '<text x="57" y="18" text-anchor="middle" fill="#38bdf8" font-family="ui-monospace,Consolas,monospace" font-size="8.5" font-weight="700">STAGE 1 · UEFI</text>'
    '<text x="8" y="38" fill="#f8fafc" font-family="system-ui,sans-serif" font-size="9" font-weight="700">Power_Good &amp; POST</text>'
    '<text x="8" y="52" fill="#cbd5e1" font-family="ui-monospace,monospace" font-size="7.8">0xFFFFFFF0 Reset</text>'
    '<text x="8" y="65" fill="#cbd5e1" font-family="ui-monospace,monospace" font-size="7.8">SEC→PEI→DXE→BDS</text>'
    '<text x="8" y="78" fill="#cbd5e1" font-family="ui-monospace,monospace" font-size="7.8">PK→KEK→db/dbx</text>'
    '<text x="8" y="91" fill="#cbd5e1" font-family="ui-monospace,monospace" font-size="7.8">TPM 2.0 PCR 0-7</text>'
    '<line x1="8" y1="102" x2="106" y2="102" stroke="#38bdf8" stroke-opacity="0.3"/>'
    '<text x="8" y="116" fill="#f87171" font-family="ui-monospace,monospace" font-size="7.6" font-weight="700">Fault: Beep/LED</text>'
    '<text x="8" y="129" fill="#94a3b8" font-family="system-ui,sans-serif" font-size="7.6">SecBoot Violation</text>'
    '</g>'
    # Stage 2
    '<g transform="translate(136,42)">'
    '<rect width="114" height="145" rx="7" fill="#0f172a" stroke="#818cf8" stroke-width="1.5"/>'
    '<rect x="6" y="6" width="102" height="18" rx="4" fill="#818cf8" fill-opacity="0.18"/>'
    '<text x="57" y="18" text-anchor="middle" fill="#818cf8" font-family="ui-monospace,Consolas,monospace" font-size="8.5" font-weight="700">STAGE 2 · GPT ESP</text>'
    '<text x="8" y="38" fill="#f8fafc" font-family="system-ui,sans-serif" font-size="9" font-weight="700">Disk &amp; Partition</text>'
    '<text x="8" y="52" fill="#cbd5e1" font-family="ui-monospace,monospace" font-size="7.8">LBA0 Prot MBR</text>'
    '<text x="8" y="65" fill="#cbd5e1" font-family="ui-monospace,monospace" font-size="7.8">LBA1 GPT Header</text>'
    '<text x="8" y="78" fill="#cbd5e1" font-family="ui-monospace,monospace" font-size="7.8">LBA2-33 Entries</text>'
    '<text x="8" y="91" fill="#cbd5e1" font-family="ui-monospace,monospace" font-size="7.8">FAT32 ESP Partition</text>'
    '<line x1="8" y1="102" x2="106" y2="102" stroke="#818cf8" stroke-opacity="0.3"/>'
    '<text x="8" y="116" fill="#f87171" font-family="ui-monospace,monospace" font-size="7.6" font-weight="700">Fault: No Boot Dev</text>'
    '<text x="8" y="129" fill="#94a3b8" font-family="system-ui,sans-serif" font-size="7.6">CSM/UEFI Mismatch</text>'
    '</g>'
    # Stage 3
    '<g transform="translate(260,42)">'
    '<rect width="114" height="145" rx="7" fill="#0f172a" stroke="#34d399" stroke-width="1.5"/>'
    '<rect x="6" y="6" width="102" height="18" rx="4" fill="#34d399" fill-opacity="0.18"/>'
    '<text x="57" y="18" text-anchor="middle" fill="#34d399" font-family="ui-monospace,Consolas,monospace" font-size="8.5" font-weight="700">STAGE 3 · BOOTMGR</text>'
    '<text x="8" y="38" fill="#f8fafc" font-family="system-ui,sans-serif" font-size="9" font-weight="700">bootmgfw.efi &amp; BCD</text>'
    '<text x="8" y="52" fill="#cbd5e1" font-family="ui-monospace,monospace" font-size="7.8">\\EFI\\Microsoft\\Boot</text>'
    '<text x="8" y="65" fill="#cbd5e1" font-family="ui-monospace,monospace" font-size="7.8">BCD Hive Store</text>'
    '<text x="8" y="78" fill="#cbd5e1" font-family="ui-monospace,monospace" font-size="7.8">{bootmgr}→{default}</text>'
    '<text x="8" y="91" fill="#cbd5e1" font-family="ui-monospace,monospace" font-size="7.8">osdevice pointer</text>'
    '<line x1="8" y1="102" x2="106" y2="102" stroke="#34d399" stroke-opacity="0.3"/>'
    '<text x="8" y="116" fill="#f87171" font-family="ui-monospace,monospace" font-size="7.6" font-weight="700">Fault: 0xc000000f</text>'
    '<text x="8" y="129" fill="#94a3b8" font-family="system-ui,sans-serif" font-size="7.6">0xc000014c BCD Bad</text>'
    '</g>'
    # Stage 4
    '<g transform="translate(384,42)">'
    '<rect width="114" height="145" rx="7" fill="#0f172a" stroke="#fbbf24" stroke-width="1.5"/>'
    '<rect x="6" y="6" width="102" height="18" rx="4" fill="#fbbf24" fill-opacity="0.18"/>'
    '<text x="57" y="18" text-anchor="middle" fill="#fbbf24" font-family="ui-monospace,Consolas,monospace" font-size="8.5" font-weight="700">STAGE 4 · WINLOAD</text>'
    '<text x="8" y="38" fill="#f8fafc" font-family="system-ui,sans-serif" font-size="9" font-weight="700">winload.efi Loader</text>'
    '<text x="8" y="52" fill="#cbd5e1" font-family="ui-monospace,monospace" font-size="7.8">Verify ci.dll / sigs</text>'
    '<text x="8" y="65" fill="#cbd5e1" font-family="ui-monospace,monospace" font-size="7.8">Load SYSTEM Hive</text>'
    '<text x="8" y="78" fill="#cbd5e1" font-family="ui-monospace,monospace" font-size="7.8">BOOT_START (0x0)</text>'
    '<text x="8" y="91" fill="#cbd5e1" font-family="ui-monospace,monospace" font-size="7.8">stornvme / ELAM</text>'
    '<line x1="8" y1="102" x2="106" y2="102" stroke="#fbbf24" stroke-opacity="0.3"/>'
    '<text x="8" y="116" fill="#f87171" font-family="ui-monospace,monospace" font-size="7.6" font-weight="700">Fault: INACCESSIBLE</text>'
    '<text x="8" y="129" fill="#94a3b8" font-family="system-ui,sans-serif" font-size="7.6">_BOOT_DEVICE BSOD</text>'
    '</g>'
    # Stage 5
    '<g transform="translate(508,42)">'
    '<rect width="114" height="145" rx="7" fill="#0f172a" stroke="#f472b6" stroke-width="1.5"/>'
    '<rect x="6" y="6" width="102" height="18" rx="4" fill="#f472b6" fill-opacity="0.18"/>'
    '<text x="57" y="18" text-anchor="middle" fill="#f472b6" font-family="ui-monospace,Consolas,monospace" font-size="8.5" font-weight="700">STAGE 5 · KERNEL</text>'
    '<text x="8" y="38" fill="#f8fafc" font-family="system-ui,sans-serif" font-size="9" font-weight="700">ntoskrnl &amp; Session</text>'
    '<text x="8" y="52" fill="#cbd5e1" font-family="ui-monospace,monospace" font-size="7.8">SYSTEM_START (0x1)</text>'
    '<text x="8" y="65" fill="#cbd5e1" font-family="ui-monospace,monospace" font-size="7.8">smss.exe → csrss</text>'
    '<text x="8" y="78" fill="#cbd5e1" font-family="ui-monospace,monospace" font-size="7.8">wininit → services</text>'
    '<text x="8" y="91" fill="#cbd5e1" font-family="ui-monospace,monospace" font-size="7.8">lsass.exe (S0) Init</text>'
    '<line x1="8" y1="102" x2="106" y2="102" stroke="#f472b6" stroke-opacity="0.3"/>'
    '<text x="8" y="116" fill="#f87171" font-family="ui-monospace,monospace" font-size="7.6" font-weight="700">Fault: 0xc000021a</text>'
    '<text x="8" y="129" fill="#94a3b8" font-family="system-ui,sans-serif" font-size="7.6">csrss / wininit die</text>'
    '</g>'
    # Stage 6
    '<g transform="translate(632,42)">'
    '<rect width="116" height="145" rx="7" fill="#0f172a" stroke="#38bdf8" stroke-width="1.5"/>'
    '<rect x="6" y="6" width="104" height="18" rx="4" fill="#38bdf8" fill-opacity="0.18"/>'
    '<text x="58" y="18" text-anchor="middle" fill="#38bdf8" font-family="ui-monospace,Consolas,monospace" font-size="8.5" font-weight="700">STAGE 6 · LOGON</text>'
    '<text x="8" y="38" fill="#f8fafc" font-family="system-ui,sans-serif" font-size="9" font-weight="700">winlogon &amp; Shell</text>'
    '<text x="8" y="52" fill="#cbd5e1" font-family="ui-monospace,monospace" font-size="7.8">LogonUI.exe Auth</text>'
    '<text x="8" y="65" fill="#cbd5e1" font-family="ui-monospace,monospace" font-size="7.8">Kerberos / NTLM</text>'
    '<text x="8" y="78" fill="#cbd5e1" font-family="ui-monospace,monospace" font-size="7.8">userinit.exe + GPO</text>'
    '<text x="8" y="91" fill="#cbd5e1" font-family="ui-monospace,monospace" font-size="7.8">explorer.exe Shell</text>'
    '<line x1="8" y1="102" x2="108" y2="102" stroke="#38bdf8" stroke-opacity="0.3"/>'
    '<text x="8" y="116" fill="#f87171" font-family="ui-monospace,monospace" font-size="7.6" font-weight="700">Fault: Black Screen</text>'
    '<text x="8" y="129" fill="#94a3b8" font-family="system-ui,sans-serif" font-size="7.6">Winlogon\\Shell key</text>'
    '</g>'
    '<text x="16" y="208" fill="#38bdf8" font-family="ui-monospace,Consolas,monospace" font-size="8.5" font-weight="700">'
    'WinRE Repair Chain: diskpart (assign S: to FAT32 ESP) → bcdboot C:\\Windows /s S: /f UEFI → bootrec /rebuildbcd → dism /RestoreHealth → sfc /scannow</text>'
    '</svg>'
    '<figcaption class="small text-muted mt-1"><strong>Windows 10/11 6-Stage UEFI/GPT Boot Architecture:</strong> Exact binary execution chain from ATX Power_Good through explorer.exe shell launch.</figcaption>'
    '</figure>'
)

LINUX_BOOT_6STAGE_SVG = (
    '<figure class="novak-boot-svg-figure" style="margin:0.9rem 0">'
    '<svg viewBox="0 0 760 215" width="100%" role="img" '
    'aria-label="Linux 6-Stage UEFI, Shim, GRUB2, initramfs, vmlinuz Kernel, and systemd Target Pipeline Diagram" '
    'class="novak-boot-pipeline-svg" style="display:block;height:auto;max-width:100%;background:#0b1120;border:1px solid rgba(52,211,153,0.35);border-radius:10px">'
    '<rect x="0" y="0" width="760" height="30" rx="10" fill="#064e3b"/>'
    '<text x="16" y="19" fill="#f8fafc" font-family="system-ui,-apple-system,sans-serif" font-size="11" font-weight="700">'
    'LINUX 6-STAGE UEFI → SHIM → GRUB2 → INITRAMFS → VMLINUZ → SYSTEMD TARGET PIPELINE</text>'
    '<text x="744" y="19" text-anchor="end" fill="#34d399" font-family="ui-monospace,Consolas,monospace" font-size="9" font-weight="700">LINUX BOOT</text>'
    # Stage 1
    '<g transform="translate(12,42)">'
    '<rect width="114" height="138" rx="7" fill="#0f172a" stroke="#34d399" stroke-width="1.5"/>'
    '<text x="57" y="18" text-anchor="middle" fill="#34d399" font-family="ui-monospace,monospace" font-size="8.5" font-weight="700">1. UEFI + SHIM</text>'
    '<text x="8" y="36" fill="#f8fafc" font-family="ui-monospace,monospace" font-size="8">shimx64.efi</text>'
    '<text x="8" y="50" fill="#cbd5e1" font-family="system-ui,sans-serif" font-size="8">ESP /boot/efi/EFI</text>'
    '<text x="8" y="64" fill="#cbd5e1" font-family="system-ui,sans-serif" font-size="8">MOK Key Validation</text>'
    '<text x="8" y="78" fill="#cbd5e1" font-family="system-ui,sans-serif" font-size="8">efibootmgr NVRAM</text>'
    '<text x="8" y="114" fill="#f87171" font-family="ui-monospace,monospace" font-size="7.6">Fix: mokutil / BIOS</text>'
    '</g>'
    # Stage 2
    '<g transform="translate(136,42)">'
    '<rect width="114" height="138" rx="7" fill="#0f172a" stroke="#38bdf8" stroke-width="1.5"/>'
    '<text x="57" y="18" text-anchor="middle" fill="#38bdf8" font-family="ui-monospace,monospace" font-size="8.5" font-weight="700">2. GRUB2STAGE</text>'
    '<text x="8" y="36" fill="#f8fafc" font-family="ui-monospace,monospace" font-size="8">grubx64.efi</text>'
    '<text x="8" y="50" fill="#cbd5e1" font-family="ui-monospace,monospace" font-size="7.8">/boot/grub/grub.cfg</text>'
    '<text x="8" y="64" fill="#cbd5e1" font-family="ui-monospace,monospace" font-size="7.8">/etc/default/grub</text>'
    '<text x="8" y="78" fill="#cbd5e1" font-family="system-ui,sans-serif" font-size="8">Kernel cmdline args</text>'
    '<text x="8" y="114" fill="#f87171" font-family="ui-monospace,monospace" font-size="7.6">Fix: grub-mkconfig</text>'
    '</g>'
    # Stage 3
    '<g transform="translate(260,42)">'
    '<rect width="114" height="138" rx="7" fill="#0f172a" stroke="#818cf8" stroke-width="1.5"/>'
    '<text x="57" y="18" text-anchor="middle" fill="#818cf8" font-family="ui-monospace,monospace" font-size="8.5" font-weight="700">3. INITRAMFS</text>'
    '<text x="8" y="36" fill="#f8fafc" font-family="ui-monospace,monospace" font-size="8">initrd.img-* cpio</text>'
    '<text x="8" y="50" fill="#cbd5e1" font-family="system-ui,sans-serif" font-size="8">RAM rootfs in RAM</text>'
    '<text x="8" y="64" fill="#cbd5e1" font-family="system-ui,sans-serif" font-size="8">Loads NVMe/LVM/LUKS</text>'
    '<text x="8" y="78" fill="#cbd5e1" font-family="ui-monospace,monospace" font-size="7.8">switch_root /sysroot</text>'
    '<text x="8" y="114" fill="#f87171" font-family="ui-monospace,monospace" font-size="7.6">Fix: update-initramfs</text>'
    '</g>'
    # Stage 4
    '<g transform="translate(384,42)">'
    '<rect width="114" height="138" rx="7" fill="#0f172a" stroke="#fbbf24" stroke-width="1.5"/>'
    '<text x="57" y="18" text-anchor="middle" fill="#fbbf24" font-family="ui-monospace,monospace" font-size="8.5" font-weight="700">4. VMLINUZ</text>'
    '<text x="8" y="36" fill="#f8fafc" font-family="ui-monospace,monospace" font-size="8">/boot/vmlinuz-*</text>'
    '<text x="8" y="50" fill="#cbd5e1" font-family="system-ui,sans-serif" font-size="8">Ring 0 Kernel Init</text>'
    '<text x="8" y="64" fill="#cbd5e1" font-family="ui-monospace,monospace" font-size="7.8">udev / /proc / /sys</text>'
    '<text x="8" y="78" fill="#cbd5e1" font-family="ui-monospace,monospace" font-size="7.8">Mount real / (ext4)</text>'
    '<text x="8" y="114" fill="#f87171" font-family="ui-monospace,monospace" font-size="7.6">Fault: Kernel Panic</text>'
    '</g>'
    # Stage 5
    '<g transform="translate(508,42)">'
    '<rect width="114" height="138" rx="7" fill="#0f172a" stroke="#f472b6" stroke-width="1.5"/>'
    '<text x="57" y="18" text-anchor="middle" fill="#f472b6" font-family="ui-monospace,monospace" font-size="8.5" font-weight="700">5. SYSTEMD PID 1</text>'
    '<text x="8" y="36" fill="#f8fafc" font-family="ui-monospace,monospace" font-size="8">/sbin/init→systemd</text>'
    '<text x="8" y="50" fill="#cbd5e1" font-family="ui-monospace,monospace" font-size="7.8">local-fs.target</text>'
    '<text x="8" y="64" fill="#cbd5e1" font-family="ui-monospace,monospace" font-size="7.8">/etc/fstab mounts</text>'
    '<text x="8" y="78" fill="#cbd5e1" font-family="ui-monospace,monospace" font-size="7.8">network.target</text>'
    '<text x="8" y="114" fill="#f87171" font-family="ui-monospace,monospace" font-size="7.6">Fix: nofail in fstab</text>'
    '</g>'
    # Stage 6
    '<g transform="translate(632,42)">'
    '<rect width="116" height="138" rx="7" fill="#0f172a" stroke="#34d399" stroke-width="1.5"/>'
    '<text x="58" y="18" text-anchor="middle" fill="#34d399" font-family="ui-monospace,monospace" font-size="8.5" font-weight="700">6. TARGETS &amp; GUI</text>'
    '<text x="8" y="36" fill="#f8fafc" font-family="ui-monospace,monospace" font-size="7.8">multi-user.target</text>'
    '<text x="8" y="50" fill="#cbd5e1" font-family="ui-monospace,monospace" font-size="7.8">graphical.target</text>'
    '<text x="8" y="64" fill="#cbd5e1" font-family="system-ui,sans-serif" font-size="8">GDM3 + GNOME Shell</text>'
    '<text x="8" y="78" fill="#cbd5e1" font-family="ui-monospace,monospace" font-size="7.8">sshd / cron daemons</text>'
    '<text x="8" y="114" fill="#34d399" font-family="ui-monospace,monospace" font-size="7.6">journalctl -xb</text>'
    '</g>'
    '<text x="16" y="198" fill="#34d399" font-family="ui-monospace,Consolas,monospace" font-size="8.5" font-weight="700">'
    'Linux Recovery CLI: grub-mkconfig -o /boot/grub/grub.cfg · update-initramfs -u -k all · dracut -f · systemctl get-default · journalctl -xb -p err</text>'
    '</svg>'
    '<figcaption class="small text-muted mt-1"><strong>Linux 6-Stage UEFI/GRUB2/initramfs/systemd Boot Pipeline:</strong> From UEFI NVRAM and Shim MOK verification to PID 1 systemd target activation.</figcaption>'
    '</figure>'
)

WINDOWS_BOOT_DEEP_DIVE_HTML = rf"""
<article class="novak-boot-deep-dive" id="novak-win-boot-deep-dive" aria-label="Windows 10/11 6-Stage Boot Architecture Deep Dive" style="margin:1.25rem 0;padding:1.25rem 1.35rem;border:1.5px solid rgba(56,189,248,0.35);border-radius:14px;background:rgba(15,23,42,0.03)">
  <div class="d-flex flex-wrap justify-content-between align-items-center gap-2 mb-2">
    <h4 style="margin:0;font-size:1.15rem;font-weight:800">Engineering Deep Dive: Windows 10/11 6-Stage UEFI/GPT &amp; Legacy BIOS Boot Architecture</h4>
    <span class="badge text-bg-primary">CompTIA A+ 220-1201 / 220-1202 · SME Reference</span>
  </div>
  <p class="mb-2">To isolate whether a non-booting PC is suffering from a motherboard power-rail fault, a UEFI/CSM firmware mismatch, a wiped EFI System Partition (ESP), a corrupted Boot Configuration Data (BCD) store, a missing storage controller driver, or a user-mode shell crash, a technician must trace the exact six-stage execution chain from hardware power-on to <code>explorer.exe</code>.</p>
  {WIN_BOOT_6STAGE_SVG}
  <div class="row g-3 mt-1">
    <div class="col-12 col-md-6">
      <div class="p-3 rounded border h-100">
        <h5 class="h6 fw-bold mb-1">Stage 1 — Power-On, Power_Good &amp; UEFI Firmware Phases (SEC → PEI → DXE → BDS)</h5>
        <p class="small mb-1">Pressing the chassis button grounds the ATX <code>PS_ON#</code> pin. Once the PSU stabilizes the <code>+12V</code>, <code>+5V</code>, and <code>+3.3V</code> rails, it asserts the <code>PWR_OK</code> (Power_Good) signal, releasing the CPU from reset at the hardware reset vector (<code>0xFFFFFFF0</code>). UEFI executes four phases:</p>
        <ul class="small mb-0">
          <li><strong>SEC (Security) &amp; PEI (Pre-EFI Initialization):</strong> Initializes CPU microcode, CAR (Cache-as-RAM), and trains DDR4/DDR5 memory channels via SPD/XMP profiles.</li>
          <li><strong>DXE (Driver Execution Environment):</strong> Enumerates PCIe/NVMe/SATA buses, populates ACPI tables, and initializes the GOP (Graphics Output Protocol) display.</li>
          <li><strong>BDS (Boot Device Selection) &amp; Secure Boot Chain:</strong> Evaluates NVRAM <code>BootOrder</code> variables and enforces <strong>UEFI Secure Boot</strong> cryptographic validation: the <strong>Platform Key (PK)</strong> trusts the <strong>Key Exchange Key (KEK)</strong>, which verifies bootloader signatures against the <strong>Authorized Signature Database (<code>db</code>)</strong> and blocks any SHA-256 hash or certificate listed in the <strong>Forbidden Signature Database (<code>dbx</code>)</strong>. Simultaneously, <strong>TPM 2.0</strong> records cryptographic hashes into <strong>PCRs 0–7</strong> (Platform Configuration Registers) before releasing the BitLocker Volume Master Key (VMK).</li>
        </ul>
      </div>
    </div>
    <div class="col-12 col-md-6">
      <div class="p-3 rounded border h-100">
        <h5 class="h6 fw-bold mb-1">Stage 2 — GPT Disk Geometry &amp; EFI System Partition (ESP) vs. Legacy BIOS/MBR</h5>
        <p class="small mb-1">Modern Windows 11 installations require <strong>UEFI + GPT (GUID Partition Table)</strong>:</p>
        <ul class="small mb-0">
          <li><strong>GPT Layout:</strong> <code>LBA 0</code> holds a Protective MBR (preventing legacy tools from overwriting the disk); <code>LBA 1</code> stores the Primary GPT Header and CRC32 checksums; <code>LBA 2–33</code> store up to 128 partition entries (supporting volumes <code>&gt; 2.2 TB</code>); and a backup GPT header sits at the final sectors of the disk.</li>
          <li><strong>FAT32 EFI System Partition (ESP):</strong> Identified by partition type GUID <code>C12A7328-F81F-11D2-BA4B-00A0C93EC93B</code> (typically 100–260 MB, formatted <code>FAT32</code>). UEFI BDS mounts this partition directly and executes <code>\EFI\Microsoft\Boot\bootmgfw.efi</code>.</li>
          <li><strong>Legacy BIOS / MBR Contrast:</strong> Legacy BIOS uses <code>INT 13h</code> real-mode interrupts to read the <code>440-byte</code> bootstrap code in <code>LBA 0</code>, parses the 4-entry <code>64-byte</code> partition table (verifying the <code>0x55AA</code> boot signature), jumps to the Active partition's Volume Boot Record (VBR), and invokes <code>bootmgr</code>. Switching UEFI to Legacy CSM on a GPT disk causes an immediate <em>No Bootable Device</em> error.</li>
        </ul>
      </div>
    </div>
    <div class="col-12 col-md-6">
      <div class="p-3 rounded border h-100">
        <h5 class="h6 fw-bold mb-1">Stage 3 — Windows Boot Manager (<code>bootmgfw.efi</code>) &amp; BCD Registry Hive</h5>
        <p class="small mb-1"><code>\EFI\Microsoft\Boot\bootmgfw.efi</code> reads the <strong>Boot Configuration Data (BCD)</strong> store located at <code>\EFI\Microsoft\Boot\BCD</code> on the FAT32 ESP (or <code>\Boot\BCD</code> on Legacy MBR):</p>
        <ul class="small mb-0">
          <li>The BCD store is a binary Windows Registry hive (mounted at <code>HKLM\BCD00000000</code>). It replaces legacy <code>boot.ini</code>.</li>
          <li>The <code>{{bootmgr}}</code> object defines <code>default</code>, <code>displayorder</code>, and <code>timeout</code>. Each OS entry (<code>{{default}}</code> / <code>{{current}}</code>) defines <code>device</code> and <code>osdevice</code> partition pointers, <code>path \Windows\System32\winload.efi</code>, <code>recoverysequence</code> (pointing to WinRE <code>winre.wim</code>), and boot flags (<code>safeboot</code>, <code>testsigning</code>, <code>nx</code>).</li>
          <li>If the system is waking from hibernation (ACPI S4), <code>bootmgfw.efi</code> branches to <code>winresume.efi</code> to stream <code>C:\hiberfil.sys</code> back into RAM.</li>
        </ul>
      </div>
    </div>
    <div class="col-12 col-md-6">
      <div class="p-3 rounded border h-100">
        <h5 class="h6 fw-bold mb-1">Stage 4 — Windows OS Loader (<code>winload.efi</code>), Code Integrity &amp; <code>BOOT_START</code></h5>
        <p class="small mb-1"><code>\Windows\System32\winload.efi</code> prepares the execution environment for the Windows kernel:</p>
        <ul class="small mb-0">
          <li><strong>Signature Verification:</strong> Invokes <code>ci.dll</code> (Code Integrity) to validate digital signatures on <code>ntoskrnl.exe</code>, <code>hal.dll</code>, and all boot-critical kernel drivers.</li>
          <li><strong>SYSTEM Registry Hive &amp; <code>SERVICE_BOOT_START (0x0)</code>:</strong> Loads <code>C:\Windows\System32\Config\SYSTEM</code> into memory BEFORE the NTFS driver is even running, scanning <code>HKLM\SYSTEM\CurrentControlSet\Services</code> for drivers with <code>Start = 0x0 (SERVICE_BOOT_START)</code>—specifically storage controllers (<code>stornvme.sys</code>, <code>storahci.sys</code>), volume managers (<code>volmgr.sys</code>, <code>partmgr.sys</code>), and the file system driver (<code>ntfs.sys</code>).</li>
          <li><strong>ELAM (Early Launch Anti-Malware):</strong> Initializes the registered ELAM driver before any third-party boot driver is allowed to execute, preventing rootkits from hijacking kernel startup.</li>
        </ul>
      </div>
    </div>
    <div class="col-12">
      <div class="p-3 rounded border">
        <h5 class="h6 fw-bold mb-1">Stage 5 — Kernel (<code>ntoskrnl.exe</code>) &amp; User-Mode Session Chain (<code>smss.exe → wininit.exe → services.exe / lsass.exe → winlogon.exe</code>)</h5>
        <p class="small mb-2">Once <code>winload.efi</code> switches the CPU paging tables and transfers control to <code>ntoskrnl.exe</code>, the kernel initializes the Executive subsystems (Memory Manager, Object Manager, I/O Manager, Security Reference Monitor, Plug-and-Play Manager), initializes <code>SERVICE_SYSTEM_START (0x1)</code> drivers (such as TCP/IP <code>tcpip.sys</code>), mounts the remaining registry hives (<code>SAM</code>, <code>SECURITY</code>, <code>SOFTWARE</code>, <code>DEFAULT</code>), and spawns the user-mode startup hierarchy:</p>
        <ol class="small mb-0">
          <li><strong>Session Manager Subsystem (<code>smss.exe</code>):</strong> The first user-mode process created by the kernel. It sets system environment variables, creates virtual memory paging files (<code>C:\pagefile.sys</code>), processes <code>PendingFileRenameOperations</code>, loads the Win32 kernel subsystem driver (<code>win32k.sys</code>), and forks into <strong>Session 0</strong> (isolated system services session) and <strong>Session 1</strong> (interactive user console session).</li>
          <li><strong>Client/Server Runtime Subsystem (<code>csrss.exe</code>) &amp; Windows Initialization (<code>wininit.exe</code>) in Session 0:</strong> <code>wininit.exe</code> launches two critical Session 0 daemons:
            <ul>
              <li><strong>Service Control Manager (<code>services.exe</code>):</strong> Reads <code>HKLM\SYSTEM\CurrentControlSet\Services</code> and starts all <code>SERVICE_AUTO_START (0x2)</code> background daemons (DHCP Client, DNS Client, Workstation, Server, Group Policy Client, Defender, Print Spooler, and <code>svchost.exe</code> service groups). Once a user signs in successfully, <code>services.exe</code> writes the current configuration to <code>LastKnownGood</code>.</li>
              <li><strong>Local Security Authority Subsystem Service (<code>lsass.exe</code>):</strong> Enforces local security policy, validates logons via Kerberos v5 tickets (domain) or NTLMv2/SAM hashes (local), generates security access tokens (SID + group memberships + privileges), and writes Security Event Log audit records (e.g., Event ID <code>4624</code> Logon Success / <code>4625</code> Failed Logon).</li>
            </ul>
          </li>
          <li><strong>Interactive Logon Manager (<code>winlogon.exe</code>) in Session 1:</strong> Spawns <code>LogonUI.exe</code> (rendering the lock screen and Credential Providers for password, PIN, smart card, or Windows Hello biometrics). After <code>lsass.exe</code> returns a valid access token, <code>winlogon.exe</code> reads <code>HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon\Userinit</code> to launch <code>userinit.exe</code>, which applies user Group Policy objects, maps logon scripts, and launches the desktop shell defined in the <code>Shell</code> value (<code>explorer.exe</code>).</li>
        </ol>
      </div>
    </div>
  </div>

  <h5 class="h6 fw-bold mt-3 mb-2">Stage 6 — Stage-by-Stage Boot Failure Diagnostics &amp; WinRE Command Playbook</h5>
  <div class="novak-spec-table-wrap" style="overflow-x:auto">
    <table class="novak-spec-table" style="width:100%;border-collapse:collapse;font-size:0.85rem">
      <thead>
        <tr style="background:rgba(56,189,248,0.12);text-align:left">
          <th style="padding:0.45rem 0.55rem">Boot Stage &amp; Component</th>
          <th style="padding:0.45rem 0.55rem">Exact Error Code / Symptom</th>
          <th style="padding:0.45rem 0.55rem">Root Cause</th>
          <th style="padding:0.45rem 0.55rem">Exact WinRE / Firmware Recovery Procedure</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td style="padding:0.45rem 0.55rem;border-bottom:1px solid rgba(148,163,184,0.2)"><strong>Stage 1–2: UEFI / ESP</strong></td>
          <td style="padding:0.45rem 0.55rem;border-bottom:1px solid rgba(148,163,184,0.2)"><code>No Bootable Device Found</code> or <code>Secure Boot Violation</code></td>
          <td style="padding:0.45rem 0.55rem;border-bottom:1px solid rgba(148,163,184,0.2)">UEFI switched to Legacy CSM on GPT disk, dead CR2032 reset CMOS, or unsigned bootloader</td>
          <td style="padding:0.45rem 0.55rem;border-bottom:1px solid rgba(148,163,184,0.2)">Set UEFI Native mode (disable CSM), verify NVMe/SATA detection in BIOS, replace CR2032 if clock reset</td>
        </tr>
        <tr>
          <td style="padding:0.45rem 0.55rem;border-bottom:1px solid rgba(148,163,184,0.2)"><strong>Stage 3: BCD Store</strong></td>
          <td style="padding:0.45rem 0.55rem;border-bottom:1px solid rgba(148,163,184,0.2)"><code>0xc000000f</code> / <code>0xc000014c</code> / <code>BOOTMGR is missing</code></td>
          <td style="padding:0.45rem 0.55rem;border-bottom:1px solid rgba(148,163,184,0.2)">Deleted or corrupted <code>\EFI\Microsoft\Boot\BCD</code> hive or wiped FAT32 ESP</td>
          <td style="padding:0.45rem 0.55rem;border-bottom:1px solid rgba(148,163,184,0.2)">In WinRE: <code>diskpart</code> → <code>sel vol &lt;ESP&gt;</code> → <code>assign letter=S:</code> → <code>exit</code> → <code>bcdboot C:\Windows /s S: /f UEFI</code> (or Legacy: <code>bootrec /fixmbr</code>, <code>bootrec /fixboot</code>, <code>bootrec /rebuildbcd</code>)</td>
        </tr>
        <tr>
          <td style="padding:0.45rem 0.55rem;border-bottom:1px solid rgba(148,163,184,0.2)"><strong>Stage 4: winload.efi</strong></td>
          <td style="padding:0.45rem 0.55rem;border-bottom:1px solid rgba(148,163,184,0.2)">BSOD <code>INACCESSIBLE_BOOT_DEVICE</code> (<code>0x0000007B</code>)</td>
          <td style="padding:0.45rem 0.55rem;border-bottom:1px solid rgba(148,163,184,0.2)">Storage mode flipped (AHCI ↔ RAID/VMD) or corrupt <code>BOOT_START</code> driver (<code>stornvme.sys</code>)</td>
          <td style="padding:0.45rem 0.55rem;border-bottom:1px solid rgba(148,163,184,0.2)">Restore SATA/NVMe controller mode (AHCI vs RAID) in UEFI, or boot Safe Mode / roll back driver in WinRE</td>
        </tr>
        <tr>
          <td style="padding:0.45rem 0.55rem;border-bottom:1px solid rgba(148,163,184,0.2)"><strong>Stage 5: Kernel / Session 0</strong></td>
          <td style="padding:0.45rem 0.55rem;border-bottom:1px solid rgba(148,163,184,0.2)">BSOD <code>0xc000021a</code> (<code>WINLOGON_FATAL_ERROR</code>)</td>
          <td style="padding:0.45rem 0.55rem;border-bottom:1px solid rgba(148,163,184,0.2)">User-mode critical process (<code>csrss.exe</code> or <code>wininit.exe</code>) terminated or corrupt system files</td>
          <td style="padding:0.45rem 0.55rem;border-bottom:1px solid rgba(148,163,184,0.2)">Run offline repair: <code>dism /Image:C:\ /Cleanup-Image /RestoreHealth</code> then <code>sfc /scannow /offbootdir=C:\ /offwindir=C:\Windows</code>, or <code>rstrui.exe</code></td>
        </tr>
        <tr>
          <td style="padding:0.45rem 0.55rem"><strong>Stage 6: Winlogon / Shell</strong></td>
          <td style="padding:0.45rem 0.55rem">Black screen with movable mouse cursor after signing in</td>
          <td style="padding:0.45rem 0.55rem"><code>explorer.exe</code> failed to launch or <code>Winlogon\Shell</code> registry value hijacked by malware</td>
          <td style="padding:0.45rem 0.55rem">Press <code>Ctrl+Shift+Esc</code> → Run new task <code>regedit</code> → verify <code>HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon\Shell = explorer.exe</code></td>
        </tr>
      </tbody>
    </table>
  </div>
</article>
"""

LINUX_BOOT_DEEP_DIVE_HTML = rf"""
<article class="novak-boot-deep-dive" id="novak-linux-boot-deep-dive" aria-label="Linux 6-Stage UEFI, GRUB2, initramfs, and systemd Boot Pipeline Deep Dive" style="margin:1.25rem 0;padding:1.25rem 1.35rem;border:1.5px solid rgba(52,211,153,0.35);border-radius:14px;background:rgba(15,23,42,0.03)">
  <div class="d-flex flex-wrap justify-content-between align-items-center gap-2 mb-2">
    <h4 style="margin:0;font-size:1.15rem;font-weight:800">Engineering Deep Dive: Linux 6-Stage Boot Pipeline (UEFI → Shim → GRUB2 → initramfs → vmlinuz → systemd)</h4>
    <span class="badge text-bg-success">CompTIA A+ 220-1202 &amp; Linux Workstation Admin</span>
  </div>
  <p class="mb-2">Understanding how Linux boots—and how it parallels the Windows UEFI/BCD/winload/ntoskrnl chain—allows you to recover broken bootloaders, missing NVMe initramfs modules, bad <code>/etc/fstab</code> mounts, and hung <code>systemd</code> targets without reinstalling the OS.</p>
  {LINUX_BOOT_6STAGE_SVG}
  <div class="row g-3 mt-1">
    <div class="col-12 col-md-6">
      <div class="p-3 rounded border h-100">
        <h5 class="h6 fw-bold mb-1">Stages 1 &amp; 2 — UEFI NVRAM, Secure Boot Shim (<code>shimx64.efi</code>) &amp; GRUB2 (<code>grubx64.efi</code>)</h5>
        <ul class="small mb-0">
          <li><strong>Stage 1 (UEFI + Shim):</strong> UEFI firmware reads NVRAM boot entries (managed in Linux via <code>efibootmgr -v</code>) and mounts the FAT32 EFI System Partition at <code>/boot/efi</code>. To work with Microsoft-signed UEFI Secure Boot, Linux distributions launch a Microsoft-signed first-stage loader (<code>/boot/efi/EFI/ubuntu/shimx64.efi</code>), which validates the distro's Machine Owner Key (MOK) before launching <code>grubx64.efi</code>.</li>
          <li><strong>Stage 2 (GRUB2):</strong> <code>grubx64.efi</code> reads <code>/boot/grub/grub.cfg</code> (which is generated from <code>/etc/default/grub</code> and scripts in <code>/etc/grub.d/</code> via <code>sudo update-grub</code> or <code>sudo grub-mkconfig -o /boot/grub/grub.cfg</code>). GRUB2 displays the boot menu and loads both the compressed kernel image and the initial RAM disk into memory.</li>
        </ul>
      </div>
    </div>
    <div class="col-12 col-md-6">
      <div class="p-3 rounded border h-100">
        <h5 class="h6 fw-bold mb-1">Stages 3 &amp; 4 — Kernel (<code>vmlinuz</code>) &amp; Initial RAM Filesystem (<code>initramfs</code> / <code>initrd.img</code>)</h5>
        <ul class="small mb-0">
          <li><strong>Stage 3 (<code>initramfs</code>):</strong> Why does Linux need <code>/boot/initrd.img-&lt;version&gt;</code> (or <code>initramfs-&lt;version&gt;.img</code>)? Just like Windows <code>winload.efi</code> must load <code>BOOT_START</code> storage drivers before mounting NTFS, the Linux kernel needs kernel modules (<code>nvme.ko</code>, <code>ext4.ko</code>, <code>xfs.ko</code>, LVM, RAID <code>mdadm</code>, or LUKS <code>cryptsetup</code>) to mount the real root filesystem. Those modules live inside the <code>initramfs</code> compressed <code>cpio</code> archive. Rebuild it after storage changes with <code>sudo update-initramfs -u -k all</code> (Debian/Ubuntu) or <code>sudo dracut -f</code> (RHEL/Fedora).</li>
          <li><strong>Stage 4 (<code>vmlinuz</code>):</strong> The compressed Linux kernel (<code>/boot/vmlinuz-&lt;version&gt;</code>) decompresses itself into Ring 0 memory, initializes hardware and virtual filesystems (<code>/proc</code>, <code>/sys</code>, <code>/dev</code> via <code>systemd-udevd</code>), mounts the real root filesystem (<code>/</code>) read-only and then read-write, and executes <code>switch_root</code>.</li>
        </ul>
      </div>
    </div>
    <div class="col-12">
      <div class="p-3 rounded border">
        <h5 class="h6 fw-bold mb-1">Stages 5 &amp; 6 — <code>systemd</code> (PID 1), Target Units &amp; Emergency Boot Recovery</h5>
        <p class="small mb-1">The kernel spawns <code>/sbin/init</code> (symlinked to <code>/lib/systemd/systemd</code>) as <strong>PID 1</strong>. Unlike legacy SysVinit sequential runlevels (<code>0–6</code>), <code>systemd</code> resolves unit dependencies in parallel across target milestones:</p>
        <ul class="small mb-0">
          <li><strong>Target Progression:</strong> <code>local-fs.target</code> (parses and mounts <code>/etc/fstab</code> volumes) → <code>sysinit.target</code> (swap, udev, sysctl) → <code>basic.target</code> (sockets, timers, D-Bus) → <code>multi-user.target</code> (CLI server mode: <code>NetworkManager.service</code>, <code>ssh.service</code>, <code>ufw.service</code>, <code>cron.service</code>; equivalent to Runlevel 3) → <code>graphical.target</code> (workstation GUI mode: launches <code>gdm3.service</code> / GNOME Display Manager and Desktop; equivalent to Runlevel 5).</li>
          <li><strong>Essential Linux Boot Diagnostics &amp; Recovery Commands:</strong>
            <code>systemctl get-default</code> / <code>sudo systemctl set-default graphical.target</code> ·
            <code>systemd-analyze blame</code> &amp; <code>systemd-analyze critical-chain</code> (pinpoint slow-booting services) ·
            <code>journalctl -xb -p err</code> (inspect current boot critical errors) ·
            If a typo in <code>/etc/fstab</code> drops the host into <strong>Emergency Mode</strong>, log in, run <code>mount -o remount,rw /</code>, fix the UUID or add <code>nofail</code> in <code>/etc/fstab</code>, run <code>systemctl daemon-reload</code>, and verify with <code>sudo mount -a</code>!</li>
        </ul>
      </div>
    </div>
  </div>
</article>
"""


def strip_boot_deep_dive(html: str) -> str:
    if not html:
        return ""
    return _BOOT_ARTICLE_RE.sub("\n", html)


def inject_boot_deep_dive_if_applicable(
    html: str, course_code: str, ch_order: int, les_order: int
) -> str:
    """Idempotently inject Windows and/or Linux boot deep-dive blocks into firmware, OS install/repair, and Linux lessons."""
    cleaned = strip_boot_deep_dive(html)
    code = (course_code or "ITSUP").upper()
    ch_i, les_i = int(ch_order), int(les_order)

    blocks = []
    if (code == "ITSUP" and (ch_i, les_i) in ((2, 2), (8, 1), (8, 2), (8, 3))) or (
        code == "CLIENT" and (ch_i, les_i) in ((1, 1), (1, 2), (1, 3))
    ):
        blocks.append(WINDOWS_BOOT_DEEP_DIVE_HTML.strip())
        if (code == "ITSUP" and (ch_i, les_i) in ((2, 2), (8, 1))) or (
            code == "CLIENT" and (ch_i, les_i) == (1, 1)
        ):
            blocks.append(LINUX_BOOT_DEEP_DIVE_HTML.strip())
    elif (code == "ITSUP" and (ch_i, les_i) == (9, 1)) or (
        code == "CLIENT" and (ch_i, les_i) == (2, 1)
    ):
        blocks.append(LINUX_BOOT_DEEP_DIVE_HTML.strip())
        blocks.append(WINDOWS_BOOT_DEEP_DIVE_HTML.strip())

    if not blocks:
        return cleaned

    payload = "\n" + "\n".join(blocks) + "\n"
    # Place after the 3rd `</section>` so it sits right in the core concept flow without touching `<section>` hashes
    closes = [m.end() for m in re.finditer(r"</section>", cleaned, flags=re.I)]
    if len(closes) >= 3:
        pos = closes[2]
        return cleaned[:pos] + payload + cleaned[pos:]
    return cleaned + payload
