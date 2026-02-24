# COPR Makefile for building packages from the Ludora monorepo
# This builds source RPMs for packages in the sources/ directory
srpm:
	cd sources/kde-ludora && \
	rpmbuild -bs \
		--define "_sourcedir $(CURDIR)/sources/kde-ludora" \
		--define "_srcrpmdir $(outdir)" \
		--define "_builddir $(CURDIR)/sources/kde-ludora" \
		kde-ludora.spec
# Future packages can be added here with additional targets or conditionals
# based on the $(spec) variable that COPR passes in
