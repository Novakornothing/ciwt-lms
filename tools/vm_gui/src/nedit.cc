/* nedit — small X11 text editor for the Novak Linux desktop (MIT). Uses FLTK. */
#include <FL/Fl.H>
#include <FL/Fl_Window.H>
#include <FL/Fl_Text_Editor.H>
#include <FL/Fl_Text_Buffer.H>
#include <FL/Fl_Menu_Bar.H>
#include <FL/Fl_File_Chooser.H>
#include <FL/fl_ask.H>
#include <string>
#include <cstring>

static Fl_Text_Buffer* buf = 0;
static Fl_Text_Editor* ed = 0;
static Fl_Window* win = 0;
static std::string path;
static int dirty = 0;

static void title() {
    std::string t = "Editor";
    if (!path.empty()) t += " — " + path;
    if (dirty) t += " *";
    win->label(t.c_str());
}

static void changed_cb(int, int, int, int, const char*, void*) { dirty = 1; title(); }

static int load_file(const char* p) {
    if (buf->loadfile(p) != 0) {
        fl_alert("Could not open %s", p);
        return 0;
    }
    path = p;
    dirty = 0;
    title();
    return 1;
}

static int save_file(const char* p) {
    if (buf->savefile(p) != 0) {
        fl_alert("Could not save %s", p);
        return 0;
    }
    path = p;
    dirty = 0;
    title();
    return 1;
}

static void save_as_cb(Fl_Widget*, void*) {
    const char* p = fl_file_chooser("Save as", "*", path.empty() ? "/root/" : path.c_str());
    if (p) save_file(p);
}

static void save_cb(Fl_Widget*, void*) {
    if (path.empty()) save_as_cb(0, 0);
    else save_file(path.c_str());
}

static void open_cb(Fl_Widget*, void*) {
    const char* p = fl_file_chooser("Open", "*", "/root/");
    if (p) load_file(p);
}

static void new_cb(Fl_Widget*, void*) {
    buf->text("");
    path.clear();
    dirty = 0;
    title();
}

static void quit_cb(Fl_Widget*, void*) { win->hide(); }

int main(int argc, char** argv) {
    Fl::scheme("gtk+");
    win = new Fl_Window(640, 440, "Editor");
    Fl_Menu_Bar* menu = new Fl_Menu_Bar(0, 0, 640, 24);
    menu->add("File/New", FL_COMMAND + 'n', new_cb);
    menu->add("File/Open...", FL_COMMAND + 'o', open_cb);
    menu->add("File/Save", FL_COMMAND + 's', save_cb);
    menu->add("File/Save as...", 0, save_as_cb);
    menu->add("File/Quit", FL_COMMAND + 'q', quit_cb);
    buf = new Fl_Text_Buffer();
    ed = new Fl_Text_Editor(0, 24, 640, 416);
    ed->buffer(buf);
    ed->textfont(FL_COURIER);
    ed->textsize(14);
    buf->add_modify_callback(changed_cb, 0);
    win->resizable(ed);
    win->end();
    win->show();
    if (argc > 1) load_file(argv[1]);
    else title();
    return Fl::run();
}
