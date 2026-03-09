Name:           libdnf5-plugin-snapper-ludora
Version:        1.0
Release:        1%{?dist}
Summary:        Ludora configuration for libdnf5-plugin-snapper
License:        MIT
URL:            https://github.com/predze/ludora
BuildArch:      noarch
Requires:       libdnf5-plugin-snapper >= 1.0
%description
Ludora-specific configuration for libdnf5-plugin-snapper.
Configures the plugin to snapshot ALL DNF transactions.
%prep
# No source
%build
# Nothing to build
%install
# No files to install - config is handled in %post
%post
# Modify the existing snapper.conf to use Ludora settings
# Only run on initial install, not upgrades
if [ $1 -eq 1 ]; then
    cat > /etc/dnf/libdnf5-plugins/snapper.conf << 'EOF'
# Ludora Configuration for DNF5 Snapper Plugin
# Snapshots ALL package transactions (not filtered)
[main]
enabled = true
dryrun = false
snapper_config = root
cleanup_algorithm = number
[filters]
# Snapshot ALL package transactions
include_packages = *
# All packages treated as important for retention
important_packages = *
EOF
fi
%postun
# Restore default config on uninstall
if [ $1 -eq 0 ]; then
    # Reinstall the upstream package to restore default config
    dnf reinstall -y libdnf5-plugin-snapper 2>/dev/null || true
fi
%files
# No files owned by this package
%changelog
* Mon Mar 09 2026 Predze <predze@ludora> - 1.0-1
- Initial Ludora configuration package
