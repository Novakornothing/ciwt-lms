/* nsettings — network, disks, firewall, users, logs, processes, packages, and SSH.
   MIT. Runs only inside the guest. Each button calls a novak-* tool that changes real system state. */
#include <FL/Fl.H>
#include <FL/Fl_Window.H>
#include <FL/Fl_Tabs.H>
#include <FL/Fl_Group.H>
#include <FL/Fl_Input.H>
#include <FL/Fl_Button.H>
#include <FL/Fl_Box.H>
#include <FL/Fl_Multiline_Output.H>
#include <FL/Fl_Browser.H>
#include <string>
#include "util.h"

static Fl_Multiline_Output* logbox;

static void note(const std::string& s) {
    logbox->value(s.c_str());
}

static void run_note(const std::string& cmd) {
    note(sh_run(cmd + " 2>&1; echo exit:$?"));
}

static Fl_Group* tab(Fl_Tabs* tabs, const char* name, int W, int H) {
    Fl_Group* g = new Fl_Group(4, 28, W - 8, H - 32, name);
    g->labelsize(13);
    return g;
}

static Fl_Input* field(int x, int y, int w, const char* label, const char* val = "") {
    Fl_Input* in = new Fl_Input(x, y, w, 22, label);
    in->labelsize(12);
    in->textsize(13);
    if (val && *val) in->value(val);
    return in;
}

int main(int argc, char** argv) {
    const int W = 640, H = 460;
    Fl::scheme("gtk+");
    Fl_Window* win = new Fl_Window(W, H, "Settings");
    Fl_Tabs* tabs = new Fl_Tabs(4, 4, W - 8, H - 78);
    tabs->labelsize(12);

    /* Network */
    {
        Fl_Group* g = tab(tabs, "Network", W, H);
        static Fl_Input *addr, *prefix, *gw, *dns, *profile;
        addr = field(110, 40, 180, "Address");
        prefix = field(110, 68, 60, "Prefix");
        prefix->value("24");
        gw = field(110, 96, 180, "Gateway");
        dns = field(110, 124, 180, "DNS");
        profile = field(110, 152, 140, "Profile");
        profile->value("guided");
        Fl_Button* save = new Fl_Button(110, 186, 140, 26, "Save profile");
        Fl_Button* apply = new Fl_Button(260, 186, 160, 26, "Apply live");
        save->callback([](Fl_Widget*, void*) {
            run_note("novak-net save " + sh_quote(profile->value()) + " " + sh_quote(addr->value()) + " " +
                     sh_quote(prefix->value()) + " " + sh_quote(gw->value()) + " " + sh_quote(dns->value()));
        });
        apply->callback([](Fl_Widget*, void*) {
            run_note("novak-net apply " + sh_quote(addr->value()) + " " + sh_quote(prefix->value()) + " " +
                     sh_quote(gw->value()) + " " + sh_quote(dns->value()));
        });
        new Fl_Box(110, 220, 480, 36, "Save profile writes /etc/novak/profiles/<name>.conf.\nApply live sets eth0, the default route, and /etc/resolv.conf.");
        g->end();
    }
    /* Disks */
    {
        Fl_Group* g = tab(tabs, "Disks", W, H);
        static Fl_Input *img, *mnt, *opts;
        img = field(120, 40, 360, "Image");
        img->value("/var/lib/novak/data.img");
        mnt = field(120, 68, 220, "Mount point");
        mnt->value("/srv/data");
        opts = field(120, 96, 220, "Options");
        opts->value("defaults,nofail");
        Fl_Button* report = new Fl_Button(120, 132, 170, 26, "Save health report");
        Fl_Button* mount = new Fl_Button(300, 132, 170, 26, "Mount and save fstab");
        report->callback([](Fl_Widget*, void*) { run_note("novak-disk report " + sh_quote(img->value())); });
        mount->callback([](Fl_Widget*, void*) {
            run_note("novak-disk mount " + sh_quote(img->value()) + " " + sh_quote(mnt->value()) + " " + sh_quote(opts->value()));
        });
        new Fl_Box(120, 168, 460, 48, "Health report reads the image size from the filesystem.\nMount uses a loop device and appends a line to /etc/fstab.");
        g->end();
    }
    /* Firewall */
    {
        Fl_Group* g = tab(tabs, "Firewall", W, H);
        static Fl_Input *port, *ban;
        Fl_Button* en = new Fl_Button(20, 44, 220, 26, "Enable drop-incoming policy");
        Fl_Button* ssh = new Fl_Button(250, 44, 160, 26, "Start SSH");
        port = field(90, 84, 80, "TCP port");
        Fl_Button* allow = new Fl_Button(180, 84, 120, 26, "Allow port");
        ban = field(90, 120, 160, "Ban IP");
        Fl_Button* banb = new Fl_Button(260, 120, 100, 26, "Ban");
        en->callback([](Fl_Widget*, void*) { run_note("novak-fw enable"); });
        ssh->callback([](Fl_Widget*, void*) { run_note("novak-fw ssh"); });
        allow->callback([](Fl_Widget*, void*) { run_note("novak-fw allow " + sh_quote(port->value())); });
        banb->callback([](Fl_Widget*, void*) { run_note("novak-fw ban " + sh_quote(ban->value())); });
        new Fl_Box(20, 160, 500, 36, "Rules are real iptables rules and are saved to /etc/iptables/rules.v4.");
        g->end();
    }
    /* Users */
    {
        Fl_Group* g = tab(tabs, "Users", W, H);
        static Fl_Input* user;
        user = field(100, 48, 160, "Username");
        Fl_Button* unlock = new Fl_Button(100, 84, 140, 26, "Unlock account");
        Fl_Button* sudo = new Fl_Button(250, 84, 160, 26, "Grant sudo");
        unlock->callback([](Fl_Widget*, void*) { run_note("novak-user unlock " + sh_quote(user->value())); });
        sudo->callback([](Fl_Widget*, void*) { run_note("novak-user sudo " + sh_quote(user->value())); });
        new Fl_Box(100, 124, 460, 48, "File permissions are changed in Files → Permissions.\nGrant sudo adds the account to the sudo group.");
        g->end();
    }
    /* Logs */
    {
        Fl_Group* g = tab(tabs, "Logs", W, H);
        static Fl_Multiline_Output* view;
        static Fl_Input* ip;
        view = new Fl_Multiline_Output(16, 40, W - 40, 150);
        view->textfont(FL_COURIER);
        view->textsize(12);
        ip = field(70, 200, 150, "Ban IP");
        Fl_Button* ref = new Fl_Button(230, 200, 90, 22, "Refresh");
        Fl_Button* ban = new Fl_Button(326, 200, 70, 22, "Ban");
        Fl_Button* rot = new Fl_Button(402, 200, 90, 22, "Rotate");
        ref->callback([](Fl_Widget*, void*) {
            view->value(sh_run("echo '--- /var/log/messages ---'; tail -n 25 /var/log/messages 2>/dev/null; echo; echo '--- /var/log/secure ---'; tail -n 15 /var/log/secure 2>/dev/null").c_str());
        });
        ban->callback([](Fl_Widget*, void*) { run_note("novak-fw ban " + sh_quote(ip->value())); });
        rot->callback([](Fl_Widget*, void*) { run_note("novak-log rotate"); });
        view->value("Press Refresh to read the logs.");
        g->end();
    }
    /* Processes */
    {
        Fl_Group* g = tab(tabs, "Processes", W, H);
        static Fl_Browser* br;
        static Fl_Input *name, *swap;
        br = new Fl_Browser(16, 40, W - 40, 140);
        br->textfont(FL_COURIER);
        br->textsize(12);
        name = field(90, 190, 160, "Name");
        Fl_Button* ref = new Fl_Button(260, 190, 90, 22, "Refresh");
        Fl_Button* stop = new Fl_Button(356, 190, 80, 22, "Stop");
        swap = field(110, 222, 50, "Swappiness");
        Fl_Button* apply = new Fl_Button(170, 222, 140, 22, "Apply swappiness");
        ref->callback([](Fl_Widget*, void*) {
            br->clear();
            std::string t = sh_run("novak-proc list");
            std::string line;
            for (size_t i = 0; i <= t.size(); i++) {
                if (i == t.size() || t[i] == '\n') {
                    if (!line.empty()) br->add(line.c_str());
                    line.clear();
                } else line += t[i];
            }
        });
        br->callback([](Fl_Widget*, void*) {
            int i = br->value();
            if (i < 1) return;
            const char* t = br->text(i);
            const char* sp = t ? strchr(t, ' ') : 0;
            if (sp) name->value(sp + 1);
        });
        stop->callback([](Fl_Widget*, void*) { run_note("novak-proc stop " + sh_quote(name->value())); });
        apply->callback([](Fl_Widget*, void*) { run_note("novak-proc swappiness " + sh_quote(swap->value())); });
        g->end();
    }
    /* Packages */
    {
        Fl_Group* g = tab(tabs, "Packages", W, H);
        static Fl_Input *pkg, *minute, *cmd;
        Fl_Button* upd = new Fl_Button(20, 44, 160, 26, "Update package index");
        pkg = field(100, 84, 140, "Package");
        Fl_Button* add = new Fl_Button(250, 84, 100, 26, "Install");
        minute = field(100, 124, 50, "Minute");
        cmd = field(100, 152, 360, "Command");
        Fl_Button* cron = new Fl_Button(100, 184, 180, 26, "Enable hourly cron");
        upd->callback([](Fl_Widget*, void*) { run_note("novak-pkg update"); });
        add->callback([](Fl_Widget*, void*) { run_note("novak-pkg add " + sh_quote(pkg->value())); });
        cron->callback([](Fl_Widget*, void*) {
            run_note("novak-pkg cron " + sh_quote(minute->value()) + " " + sh_quote(cmd->value()));
        });
        new Fl_Box(20, 220, 520, 32, "The cron line is: <minute> * * * * <command>  (every hour at that minute).");
        g->end();
    }
    /* SSH */
    {
        Fl_Group* g = tab(tabs, "SSH", W, H);
        static Fl_Input *user, *port;
        Fl_Button* key = new Fl_Button(20, 44, 180, 26, "Generate Ed25519 key");
        Fl_Button* hard = new Fl_Button(210, 44, 250, 26, "Root login off, passwords off");
        user = field(110, 86, 140, "Allow user");
        Fl_Button* allow = new Fl_Button(260, 86, 100, 26, "Allow");
        port = field(110, 122, 70, "Port");
        Fl_Button* setp = new Fl_Button(190, 122, 100, 26, "Set port");
        Fl_Button* check = new Fl_Button(300, 122, 140, 26, "Check config");
        key->callback([](Fl_Widget*, void*) { run_note("novak-ssh keygen"); });
        hard->callback([](Fl_Widget*, void*) { run_note("novak-ssh harden"); });
        allow->callback([](Fl_Widget*, void*) { run_note("novak-ssh allow " + sh_quote(user->value())); });
        setp->callback([](Fl_Widget*, void*) { run_note("novak-ssh port " + sh_quote(port->value())); });
        check->callback([](Fl_Widget*, void*) { run_note("novak-ssh check"); });
        g->end();
    }

    tabs->end();
    logbox = new Fl_Multiline_Output(8, H - 70, W - 16, 62);
    logbox->textfont(FL_COURIER);
    logbox->textsize(12);
    logbox->value("Ready.");
    win->end();
    win->show();
    return Fl::run();
}
