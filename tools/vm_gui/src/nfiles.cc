/* nfiles — file manager for the Novak Linux desktop (MIT). Uses FLTK. */
#include <FL/Fl.H>
#include <FL/Fl_Window.H>
#include <FL/Fl_Browser.H>
#include <FL/Fl_Button.H>
#include <FL/Fl_Input.H>
#include <FL/Fl_Box.H>
#include <FL/Fl_Check_Button.H>
#include <FL/fl_ask.H>
#include <sys/stat.h>
#include <dirent.h>
#include <unistd.h>
#include <pwd.h>
#include <grp.h>
#include <cstring>
#include <string>
#include <vector>
#include <algorithm>
#include "util.h"

static Fl_Window* win;
static Fl_Input* path_in;
static Fl_Browser* listb;
static Fl_Box* status;
static std::string cwd = "/root";
static std::vector<std::string> names;

struct Row { std::string name; bool dir; mode_t mode; };

static std::string joinp(const std::string& dir, const std::string& name) {
    if (dir == "/") return "/" + name;
    return dir + "/" + name;
}

static std::string mode_str(mode_t m) {
    const char* r = "rwxrwxrwx";
    std::string s = (S_ISDIR(m) ? "d" : "-");
    for (int i = 0; i < 9; i++) s += (m & (0400 >> i)) ? r[i] : '-';
    char oct[8];
    snprintf(oct, sizeof oct, " %03o", (unsigned)(m & 0777));
    return s + oct;
}

static void set_status(const std::string& s) { status->copy_label(s.c_str()); }

static void refresh() {
    listb->clear();
    names.clear();
    path_in->value(cwd.c_str());
    DIR* d = opendir(cwd.c_str());
    if (!d) { set_status("Cannot open this folder"); return; }
    std::vector<Row> rows;
    struct dirent* de;
    while ((de = readdir(d))) {
        if (strcmp(de->d_name, ".") == 0) continue;
        Row r;
        r.name = de->d_name;
        std::string full = joinp(cwd, r.name);
        struct stat st;
        if (lstat(full.c_str(), &st) != 0) continue;
        r.dir = S_ISDIR(st.st_mode);
        r.mode = st.st_mode;
        rows.push_back(r);
    }
    closedir(d);
    std::sort(rows.begin(), rows.end(), [](const Row& a, const Row& b) {
        if (a.dir != b.dir) return a.dir > b.dir;
        return a.name < b.name;
    });
    for (size_t i = 0; i < rows.size(); i++) {
        char line[512];
        snprintf(line, sizeof line, "%s  %-12s  %s", rows[i].dir ? "dir " : "file",
                 mode_str(rows[i].mode).c_str(), rows[i].name.c_str());
        listb->add(line);
        names.push_back(rows[i].name);
    }
    char st[80];
    snprintf(st, sizeof st, "%d items", (int)rows.size());
    set_status(st);
}

static std::string selected_name() {
    int i = listb->value();
    if (i < 1 || i > (int)names.size()) return "";
    return names[i - 1];
}

static void go(const std::string& p) {
    char buf[512];
    if (!realpath(p.c_str(), buf)) { set_status("No such folder"); return; }
    struct stat st;
    if (stat(buf, &st) != 0 || !S_ISDIR(st.st_mode)) { set_status("Not a folder"); return; }
    cwd = buf;
    refresh();
}

static void up_cb(Fl_Widget*, void*) {
    if (cwd == "/") return;
    std::string p = cwd;
    size_t s = p.find_last_of('/');
    go(s == 0 ? "/" : p.substr(0, s));
}

static void open_sel() {
    std::string name = selected_name();
    if (name.empty() || name == ".") return;
    if (name == "..") { up_cb(0, 0); return; }
    std::string full = joinp(cwd, name);
    struct stat st;
    if (stat(full.c_str(), &st) != 0) return;
    if (S_ISDIR(st.st_mode)) go(full);
    else sh_run("nedit " + sh_quote(full) + " >/dev/null 2>&1 &");
}

static void list_cb(Fl_Widget*, void*) {
    if (Fl::event_clicks()) open_sel();
}

static void go_cb(Fl_Widget*, void*) { go(path_in->value()); }

static void edit_cb(Fl_Widget*, void*) { open_sel(); }

static void term_cb(Fl_Widget*, void*) {
    sh_run("xterm -fn 7x14 -geometry 80x24 -e sh -c 'cd " + sh_quote(cwd) + " && exec sh' >/dev/null 2>&1 &");
}

static void mkdir_cb(Fl_Widget*, void*) {
    const char* n = fl_input("New folder name");
    if (!n || !*n) return;
    std::string full = joinp(cwd, n);
    if (mkdir(full.c_str(), 0755) != 0) fl_alert("Could not create folder");
    refresh();
}

static void rename_cb(Fl_Widget*, void*) {
    std::string name = selected_name();
    if (name.empty() || name == "..") return;
    const char* n = fl_input("New name", name.c_str());
    if (!n || !*n) return;
    if (rename(joinp(cwd, name).c_str(), joinp(cwd, n).c_str()) != 0) fl_alert("Could not rename");
    refresh();
}

static void delete_cb(Fl_Widget*, void*) {
    std::string name = selected_name();
    if (name.empty() || name == "..") return;
    if (!fl_choice("Delete %s?", "Cancel", "Delete", 0, name.c_str())) return;
    std::string full = joinp(cwd, name);
    struct stat st;
    if (lstat(full.c_str(), &st) == 0 && S_ISDIR(st.st_mode)) {
        if (rmdir(full.c_str()) != 0) fl_alert("Folder is not empty, or could not be removed");
    } else if (unlink(full.c_str()) != 0) fl_alert("Could not delete");
    refresh();
}

static Fl_Check_Button* bits[9];
static int perm_apply;

static void perm_ok(Fl_Widget* w, void*) { perm_apply = 1; w->window()->hide(); }
static void perm_cancel(Fl_Widget* w, void*) { perm_apply = 0; w->window()->hide(); }

static void perm_cb(Fl_Widget*, void*) {
    std::string name = selected_name();
    if (name.empty() || name == "..") { fl_alert("Select a file first"); return; }
    std::string full = joinp(cwd, name);
    struct stat st;
    if (stat(full.c_str(), &st) != 0) return;
    perm_apply = 0;
    Fl_Window* d = new Fl_Window(300, 230, "Permissions");
    const char* labs[] = {"Owner read", "Owner write", "Owner execute",
                          "Group read", "Group write", "Group execute",
                          "Others read", "Others write", "Others execute"};
    for (int i = 0; i < 9; i++) {
        bits[i] = new Fl_Check_Button(16, 8 + i * 20, 270, 20, labs[i]);
        if (st.st_mode & (0400 >> i)) bits[i]->value(1);
    }
    Fl_Button* ok = new Fl_Button(16, 196, 120, 24, "Apply");
    Fl_Button* cancel = new Fl_Button(160, 196, 120, 24, "Cancel");
    ok->callback(perm_ok);
    cancel->callback(perm_cancel);
    d->end();
    d->set_modal();
    d->show();
    while (d->shown()) Fl::wait();
    if (perm_apply) {
        mode_t mode = 0;
        for (int i = 0; i < 9; i++) if (bits[i]->value()) mode |= (0400 >> i);
        if (chmod(full.c_str(), mode) != 0) fl_alert("Could not change permissions");
    }
    Fl::delete_widget(d);
    refresh();
}

int main(int argc, char** argv) {
    if (argc > 1) cwd = argv[1];
    Fl::scheme("gtk+");
    win = new Fl_Window(640, 460, "Files");
    path_in = new Fl_Input(8, 8, 470, 24);
    Fl_Button* go = new Fl_Button(484, 8, 70, 24, "Go");
    Fl_Button* up = new Fl_Button(560, 8, 72, 24, "Up");
    go->callback(go_cb);
    up->callback(up_cb);
    path_in->when(FL_WHEN_ENTER_KEY);
    path_in->callback(go_cb);
    listb = new Fl_Browser(8, 40, 624, 360);
    listb->type(FL_HOLD_BROWSER);
    listb->textfont(FL_COURIER);
    listb->textsize(13);
    listb->callback(list_cb);
    Fl_Button* bopen = new Fl_Button(8, 408, 80, 24, "Open");
    Fl_Button* bedit = new Fl_Button(92, 408, 80, 24, "Edit");
    Fl_Button* bterm = new Fl_Button(176, 408, 90, 24, "Terminal");
    Fl_Button* bnew = new Fl_Button(270, 408, 70, 24, "Folder");
    Fl_Button* bren = new Fl_Button(344, 408, 80, 24, "Rename");
    Fl_Button* bdel = new Fl_Button(428, 408, 70, 24, "Delete");
    Fl_Button* bperm = new Fl_Button(502, 408, 130, 24, "Permissions");
    bopen->callback([](Fl_Widget*, void*) { open_sel(); });
    bedit->callback(edit_cb);
    bterm->callback(term_cb);
    bnew->callback(mkdir_cb);
    bren->callback(rename_cb);
    bdel->callback(delete_cb);
    bperm->callback(perm_cb);
    status = new Fl_Box(8, 436, 624, 18, "");
    status->align(FL_ALIGN_LEFT | FL_ALIGN_INSIDE);
    status->labelsize(12);
    win->resizable(listb);
    win->end();
    win->show();
    refresh();
    return Fl::run();
}
