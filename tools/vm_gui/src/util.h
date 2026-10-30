/* Shared helpers for the Novak desktop tools (MIT). Guest-only; not linked into the LMS. */
#pragma once
#include <string>
#include <cstdio>
#include <cstdlib>

static inline std::string sh_quote(const std::string& s) {
    std::string o = "'";
    for (size_t i = 0; i < s.size(); i++) {
        if (s[i] == '\'') o += "'\\''";
        else if (s[i] == '\n' || s[i] == '\r') o += ' ';
        else o += s[i];
    }
    return o + "'";
}

static inline std::string sh_run(const std::string& cmd) {
    std::string out;
    FILE* f = popen(cmd.c_str(), "r");
    if (!f) return "could not run command";
    char buf[512];
    while (fgets(buf, sizeof buf, f)) {
        out += buf;
        if (out.size() > 8000) break;
    }
    int rc = pclose(f);
    if (rc != 0 && out.empty()) out = "command failed";
    return out;
}
