# Copyright (C) 2020 Tasos Alvas <tasos.alvas@qwertyuiopia.com>
# Copyright (C) 2020 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

# DebOps Logo Makefile
# See https://docs.debops.org/en/master/meta/logo.html for build requirements

BUILDDIR = .
SRCDIR = src

SVG_TARGETS = $(patsubst $(SRCDIR)/%-src.svg,$(BUILDDIR)/%.svg,$(wildcard $(SRCDIR)/*-src.svg))

.PHONY: clean all
all: clean debops.png debops-text.png debops-small.png favicon.ico $(SVG_TARGETS)

# Optimized SVG: Use these unless forced to do otherwise
$(BUILDDIR)/%.svg: $(SRCDIR)/%-src.svg
	svgo $< -o $@

# PNG with text
debops-text.png: $(SRCDIR)/debops-src.svg
	inkscape $< -h 200 -o $@

# PNG without text -- unfortunately grabbed by object ID, not layer name :(
debops.png: $(SRCDIR)/debops-src.svg
	inkscape $< -i layer9 -h 200 -o $@

# Small icon
debops-small.png: $(SRCDIR)/debops-small-src.svg
	inkscape $< -h 50 -o $@

# Favicon in multiple resolutions for anything from retina to legacy IE
favicon.ico: $(SRCDIR)/debops-small-src.svg
	inkscape $< -h 196 -o debops-small-tmp.png
	convert debops-small-tmp.png -define icon:auto-resize=196,128,64,32,16 $@
	rm debops-small-tmp.png

clean:
	rm -f ./*.png ./*.svg ./.ico
