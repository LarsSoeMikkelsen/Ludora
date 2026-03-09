Name:           libdnf5-plugin-snapper-ludora
Version:        1.0
Release:        1%{?dist}
Summary:        Ludora configuration for libdnf5-plugin-snapper
License:        MIT
URL:            https://github.com/predze/ludora
BuildArch:      noarch

# Main plugin must be installed
Requires:       libdnf5-plugin-snapper >= 1.0
%description
Ludora-specific configuration for libdnf5-plugin-snapper.
Configures the plugin to snapshot ALL DNF transactions instead
of filtering to important packages only.
%prep
# No source to prep
%build
# Nothing to build
%install
mkdir -p %{buildroot}%{_sysconfdir}/dnf/libdnf5-plugins
cat > %{buildroot}%{_sysconfdir}/dnf/libdnf5-plugins/snapper.conf << 'EOF'
# Ludora Configuration for DNF5 Snapper Plugin
# Snapshots ALL package transactions (not filtered)
[main]
# Enable the plugin
enabled = true
# Dry-run mode: show what would be done without creating snapshots
dryrun = false
# Snapper configuration to use
snapper_config = root
# Cleanup algorithm for snapshots
cleanup_algorithm = number
[filters]
# Snapshot ALL package transactions
# Setting to * means every dnf install/update/remove creates snapshots
include_packages = *
# No package exclusions - snapshot everything
# exclude_packages = 
# All packages treated as important for retention purposes
# This ensures snapshots are kept according to cleanup_algorithm
important_packages = *
EOF
%files
%config(noreplace) %{_sysconfdir}/dnf/libdnf5-plugins/snapper.conf
%changelog
* Mon Mar 09 2026 Predze <predze@ludora> - 1.0-1
- Initial Ludora configuration package
- Configures plugin to snapshot all DNF transactions
