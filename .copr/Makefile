# COPR Makefile for building packages from the Ludora monorepo
srpm:
	cd $(CURDIR) && \
	tar czf /tmp/kde-ludora-1.0.tar.gz \
		--transform 's|^|kde-ludora-1.0/|' \
		look-and-feel wallpaper icons && \
	rpmbuild -bs \
		--define "_sourcedir /tmp" \
		--define "_srcrpmdir $(outdir)" \
		--define "_builddir $(CURDIR)" \
		$(spec)
