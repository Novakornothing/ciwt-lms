/* nbg — paint the Fluxbox root so the desktop is visible on the Bochs framebuffer.
 * MIT. Linked only inside the guest, against the guest's libX11. */
#include <X11/Xlib.h>
#include <stdio.h>
#include <string.h>

int main(void) {
    Display *d = XOpenDisplay(NULL);
    if (!d) return 1;
    int s = DefaultScreen(d);
    Window r = RootWindow(d, s);
    Colormap cm = DefaultColormap(d, s);
    XColor want, exact;
    unsigned long bg = BlackPixel(d, s);
    if (XAllocNamedColor(d, cm, "#1B4F72", &want, &exact)) bg = want.pixel;
    XFontStruct *f = XLoadQueryFont(d, "7x14");
    if (!f) f = XLoadQueryFont(d, "fixed");
    GC gc = XCreateGC(d, r, 0, NULL);
    XSetForeground(d, gc, bg);
    XFillRectangle(d, r, gc, 0, 0, DisplayWidth(d, s), DisplayHeight(d, s));
    if (f) XSetFont(d, gc, f->fid);
    XSetForeground(d, gc, WhitePixel(d, s));
    const char *msg = "Novak Linux - right-click for Terminal, Files, Editor";
    XDrawString(d, r, gc, 24, 36, msg, (int)strlen(msg));
    XFlush(d);
    XSync(d, False);
    return 0;
}
