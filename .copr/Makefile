srpm:
	@if echo "$(spec)" | grep -q "kde-ludora"; then \
		cd $(CURDIR) && \
		tar czf /tmp/kde-ludora-1.4.tar.gz \
			--transform 's|^|kde-ludora-1.4/|' \
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
		tar czf /tmp/calamares-config-ludora-1.0.tar.gz \
			--transform 's|^|calamares-config-ludora-1.0/|' \
			settings.conf modules branding && \
		rpmbuild -bs \
			--define "_sourcedir /tmp" \
			--define "_srcrpmdir $(outdir)" \
			--define "_builddir $(CURDIR)" \
			$(spec); \
	elif echo "$(spec)" | grep -q "snapper-config-ludora"; then \
		cd $(CURDIR) && \
		tar czf /tmp/snapper-config-ludora-1.3.tar.gz \
			--transform 's|^|snapper-config-ludora-1.3/|' \
			ludora-snapper-setup.service \
			ludora-snapper-setup.sh \
			snapper-rollback && \
		rpmbuild -bs \
			--define "_sourcedir /tmp" \
			--define "_srcrpmdir $(outdir)" \
			--define "_builddir $(CURDIR)" \
			$(spec); \
	elif echo "$(spec)" | grep -q "snapper-actions-ludora"; then \
		cd $(CURDIR) && \
		tar czf /tmp/snapper-actions-ludora-1.0.tar.gz \
			--transform 's|^|snapper-actions-ludora-1.0/|' \
			actions.conf \
			snapper.actions \
			grub-btrfs-config && \
		rpmbuild -bs \
			--define "_sourcedir /tmp" \
			--define "_srcrpmdir $(outdir)" \
			--define "_builddir $(CURDIR)" \
			$(spec); \
	elif echo "$(spec)" | grep -q "desktop-defaults-ludora"; then \
		cd $(CURDIR) && \
		tar czf /tmp/desktop-defaults-ludora-1.0.tar.gz \
			--transform 's|^|desktop-defaults-ludora-1.0/|' \
			kdeglobals \
			plasmashellrc \
			49-nopasswd-wheel.rules \
			ludora-fastfetch.sh \
			ludora-apply-theme.sh \
			apply-ludora-theme-to-users.sh && \
		rpmbuild -bs \
			--define "_sourcedir /tmp" \
			--define "_srcrpmdir $(outdir)" \
			--define "_builddir $(CURDIR)" \
			$(spec); \
	fi
