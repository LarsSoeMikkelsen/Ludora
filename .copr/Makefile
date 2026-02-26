srpm:
	@if echo "$(spec)" | grep -q "kde-ludora"; then \
		cd $(CURDIR) && \
		tar czf /tmp/kde-ludora-1.1.tar.gz \
			--transform 's|^|kde-ludora-1.1/|' \
			look-and-feel color-schemes icons && \
		rpmbuild -bs \
			--define "_sourcedir /tmp" \
			--define "_srcrpmdir $(outdir)" \
			--define "_builddir $(CURDIR)" \
			$(spec); \
	elif echo "$(spec)" | grep -q "fastfetch-settings"; then \
		cd $(CURDIR) && \
		tar czf /tmp/fastfetch-settings-1.0.tar.gz \
			--transform 's|^|fastfetch-settings-1.0/|' \
			ludora.txt config.jsonc && \
		rpmbuild -bs \
			--define "_sourcedir /tmp" \
			--define "_srcrpmdir $(outdir)" \
			--define "_builddir $(CURDIR)" \
			$(spec); \
	fi
