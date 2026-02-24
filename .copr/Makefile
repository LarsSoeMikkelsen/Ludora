# COPR Makefile for building packages from the Ludora monorepo
# COPR runs this from the repository root, but the working directory
# when make is invoked is already in the subdirectory specified in COPR settings
srpm:
	rpmbuild -bs \
		--define "_sourcedir $(CURDIR)" \
		--define "_srcrpmdir $(outdir)" \
		--define "_builddir $(CURDIR)" \
		$(spec)
# Future packages can be added here with additional targets or conditionals
# based on the $(spec) variable that COPR passes in
