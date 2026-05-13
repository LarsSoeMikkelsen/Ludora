srpm:
	@if echo "$(spec)" | grep -q "kde-ludora"; then \
		cd $(CURDIR) && \
		tar czf /tmp/kde-ludora-1.7.tar.gz \
			--transform 's|^|kde-ludora-1.7/|' \
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
	elif echo "$(spec)" | grep -q "plymouth-ludora"; then \
		cp $(CURDIR)/watermark.png /tmp/watermark.png && \
		rpmbuild -bs \
			--define "_sourcedir /tmp" \
			--define "_srcrpmdir $(outdir)" \
			--define "_builddir $(CURDIR)" \
			$(spec); \
	elif echo "$(spec)" | grep -q "calamares-config-ludora"; then \
		cd $(CURDIR) && \
		tar czf /tmp/calamares-config-ludora-1.8.tar.gz \
			--transform 's|^|calamares-config-ludora-1.8/|' \
			settings.conf modules branding scripts && \
		rpmbuild -bs \
			--define "_sourcedir /tmp" \
			--define "_srcrpmdir $(outdir)" \
			--define "_builddir $(CURDIR)" \
			$(spec); \
	elif echo "$(spec)" | grep -q "snapper-config-ludora"; then \
		cd $(CURDIR) && \
		tar czf /tmp/snapper-config-ludora-1.8.tar.gz \
			--transform 's|^|snapper-config-ludora-1.8/|' \
			ludora-snapper-setup.service \
			ludora-snapper-setup.sh \
			snapper-commit \
			ludora-snapshot-notify.sh \
			ludora-snapshot-notify.desktop \
			ludora-snapshot-commit.desktop && \
		rpmbuild -bs \
			--define "_sourcedir /tmp" \
			--define "_srcrpmdir $(outdir)" \
			--define "_builddir $(CURDIR)" \
			$(spec); \
		elif echo "$(spec)" | grep -q "desktop-defaults-ludora"; then \
		cd $(CURDIR) && \
		tar czf /tmp/desktop-defaults-ludora-1.1.tar.gz \
			--transform 's|^|desktop-defaults-ludora-1.1/|' \
			ludora-fastfetch.sh \
			ludora-apply-theme.sh \
			apply-ludora-theme-to-users.sh && \
		rpmbuild -bs \
			--define "_sourcedir /tmp" \
			--define "_srcrpmdir $(outdir)" \
			--define "_builddir $(CURDIR)" \
			$(spec); \
	elif echo "$(spec)" | grep -q "ludora-welcome"; then \
		_dir=$$(dirname $(spec)) && \
		tar czf /tmp/ludora-welcome-1.0.tar.gz \
			-C $$_dir \
			--transform 's|^|ludora-welcome-1.0/|' \
			ludora-welcome.py \
			ludora-welcome.desktop \
			ludora-welcome-app.desktop && \
		rpmbuild -bs \
			--define "_sourcedir /tmp" \
			--define "_srcrpmdir $(outdir)" \
			--define "_builddir $$_dir" \
			$(spec); \
	fi
