Alto: a music theory trainer
============================

This folder is the Linux download of Alto. It carries its own Python and Qt, so nothing else needs installing.

Install (for you only, no root needed)

    sh install.sh install

This copies Alto to ~/.local/opt/alto, links it as ~/.local/bin/alto, and adds "Alto" to your application menu.

Update

Unpack the newer download and run `sh install.sh install` again. It replaces the program and keeps your data.

Uninstall

    sh install.sh uninstall            removes Alto, and keeps your practice history and settings
    sh install.sh uninstall --purge    removes those too

Your practice history is ~/.local/share/Alto/alto.db and your settings are in ~/.config/alto. Use "Export backup..." in Alto's menu
first if you might want them back.

If Alto does not start, run it from a terminal (~/.local/opt/alto/alto) to see why, and tell us what it printed at
https://github.com/altosaurus/alto/issues, with the name and version of your Linux.

Files

    LICENSE, THIRD_PARTY_NOTICES.md   Alto's licence, and the licences of the fonts and recordings it carries

https://github.com/altosaurus/alto
