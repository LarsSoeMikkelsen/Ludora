# COPR Makefile for building packages from the Ludora monorepo
srpm:
	@if echo "$(spec)" | grep -q "kde-ludora"; then \
		cd $(CURDIR)/sources/kde-ludora && \
		tar czf /tmp/kde-ludora-1.0.tar.gz \
			--transform 's|^|kde-ludora-1.0/|' \
			look-and-feel wallpaper icons && \
		rpmbuild -bs \
			--define "_sourcedir /tmp" \
			--define "_srcrpmdir $(outdir)" \
			--define "_builddir $(CURDIR)/sources/kde-ludora" \
			$(spec); \
	elif echo "$(spec)" | grep -q "fastfetch-settings"; then \
		cd $(CURDIR)/sources/fastfetch-settings && \
		tar czf /tmp/fastfetch-settings-1.0.tar.gz \
			--transform 's|^|fastfetch-settings-1.0/|' \
			ludora.txt config.jsonc && \
		rpmbuild -bs \
			--define "_sourcedir /tmp" \
			--define "_srcrpmdir $(outdir)" \
			--define "_builddir $(CURDIR)/sources/fastfetch-settings" \
			$(spec); \
	fi
