# Build of the cooperatio manual.
#
#   make            -> manual.md (concatenated source), diagrams (SVG + PDF),
#                      build/manual.tex and manual.pdf
#   make md         -> only manual.md
#   make diagrams   -> only the Graphviz renders
#   make check      -> margin overflow check of the PDF (needs the local tool)
#   make clean
#
# Requirements: pandoc 3 or later, graphviz (dot), lualatex (TeX Live 2025
# or later, with the TeX Gyre fonts), python3 for nothing — the manual is
# plain Markdown. The Mermaid blocks of the Markdown are rendered natively
# by viewers that support Mermaid; the PDF build swaps each one for its
# Graphviz twin (filters/mermaid.lua), so no Mermaid renderer is needed.

PANDOC   ?= pandoc
DOT      ?= dot
ENGINE   ?= lualatex

SRC      := $(sort $(wildcard src/*.md))
DOTS     := $(sort $(wildcard diagrams/*.dot))
SVGS     := $(DOTS:.dot=.svg)
PDFS     := $(DOTS:.dot=.pdf)

MAINFONT ?= TeX Gyre Pagella
SANSFONT ?= TeX Gyre Heros
MONOFONT ?= DejaVu Sans Mono

PANDOC_FLAGS := --from markdown+smart --toc --toc-depth=2 --number-sections \
    --lua-filter=filters/mermaid.lua --syntax-highlighting=tango \
    -V mainfont="$(MAINFONT)" -V sansfont="$(SANSFONT)" -V monofont="$(MONOFONT)" \
    -V geometry:a4paper -V geometry:margin=25mm -V fontsize=10pt \
    -V linkcolor=NavyBlue -V urlcolor=NavyBlue -V toccolor=black \
    -V colorlinks=true -V documentclass=report \
    --include-in-header=filters/header.tex --resource-path=.

.PHONY: all md diagrams pdf tex check clean

all: md diagrams tex pdf

md: manual.md

manual.md: $(SRC)
	cat $(SRC) > $@

diagrams: $(SVGS) $(PDFS)

diagrams/%.svg: diagrams/%.dot
	$(DOT) -Tsvg $< -o $@

diagrams/%.pdf: diagrams/%.dot
	$(DOT) -Tpdf $< -o $@

tex: build/manual.tex

build/manual.tex: manual.md $(PDFS) filters/mermaid.lua filters/header.tex
	@mkdir -p build
	$(PANDOC) $(PANDOC_FLAGS) --standalone manual.md -o $@

pdf: manual.pdf

manual.pdf: manual.md $(PDFS) filters/mermaid.lua filters/header.tex
	$(PANDOC) $(PANDOC_FLAGS) --pdf-engine=$(ENGINE) manual.md -o $@

check: manual.pdf
	python3 $(HOME)/bin/check_pdf_margins.py --pdf manual.pdf --out build/overflow

clean:
	rm -f manual.md manual.pdf build/manual.tex $(SVGS) $(PDFS)
