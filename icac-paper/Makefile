# Config

OUTDIR      := out.o
TEXINPUTS	:= .:mystyles:
export TEXINPUTS
BSTINPUTS	:= .:mystyles:
export BSTINPUTS

#################################################################
# Additional commands

# A latex command that strips graphics
PDFLATEX = pdflatex --shell-escape -interaction=nonstopmode -halt-on-error -no-parse-first-line -file-line-error

#################################################################
# Top level rules

.PHONY: clean pdf preview

all:
	@echo "Choose a target:"
	@echo "  make pdf       fully regenerate PDF"
	@echo "  make preview   interactively regenerated PDF"
	@echo "  make clean     clean intermediate files"

pdf: icac.pdf

preview: pdf
	# Requires inotify-tools
	okular icac.pdf &
	cd out.o; \
	while true; do \
		sleep 1; \
		inotifywait -e close_write -- ../* ../*/*; \
		BIBINPUTS=..: BSTINPUTS=..: bibtex icac; \
		TEXINPUTS=..: $(PDFLATEX) icac.tex; \
		cp icac.pdf ..; \
	done

clean:
	$(RM) -rf $(OUTDIR)

#################################################################
# Graphics

%.pdf: %.jpg
	convert $< $@

%.precrop.pdf: %.plot %.data
	(echo 'set term postscript color enhanced "Times" 16'; cat $<) | \
		gnuplot - | \
		epstopdf --filter --autorotate=All --hires > $@

%.eps: %.fig
	fig2dev -L eps $< > $@

%.eps: %.dia
	dia --export=$@ $<

%.eps: %.odg
	soffice -headless -norestore OdgToEps.odg "macro://OdgToEps/Standard.Convert.OdgToEps(\"$$PWD/$*\")"

# For when XeLaTeX will be more complete
#%.pdf: %.eps
#	ps2pdf -dEPSCrop $< $@

%.precrop.pdf: %.eps
	ps2pdf -sPAPERSIZE=a0 $< $@

img/%.pdf: img/%.precrop.pdf
	pdfcrop $< $@

img/%.eps::
	@echo Missing image $@
	@false

#################################################################
# Latex files

icac.pdf: $(OUTDIR)/icac.pdf
	cp $< $@

$(OUTDIR)/icac.pdf: *.bib *.sty *.tex sec/*.tex img/*.tex
	mkdir -p out.o
	cd out.o; TEXINPUTS=..: $(PDFLATEX) icac.tex
	cd out.o; BIBINPUTS=..: BSTINPUTS=..: bibtex icac
	cd out.o; TEXINPUTS=..: $(PDFLATEX) icac.tex
	cd out.o; TEXINPUTS=..: $(PDFLATEX) icac.tex
