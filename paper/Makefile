all:	ifac.tex ifac.bib ifacconf.bst ifacconf.cls
	rm -f ifac.pdf
	latex ifac.tex
	bibtex ifac.aux
	latex ifac.tex
	latex ifac.tex
	dvips -Ppdf -G0 -ta4 ifac
	ps2pdf -dCompatibilityLevel=1.4 -dMaxSubsetPct=100 -dSubsetFonts=true -dEmbedAllFonts=true -sPAPERSIZE=a4 ifac.ps ifac.pdf
	mkdir -p out.o
	rm -rf auto
	mv ifac.auxlock ifac.ps ifac.dvi ifac.aux ifac.bbl ifac.blg ifac.log ./out.o

clean:
	rm -rf out.o
	rm -f ifac.pdf
