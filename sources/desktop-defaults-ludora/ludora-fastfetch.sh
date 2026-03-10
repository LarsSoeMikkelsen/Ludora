# Ludora: Show system info with fastfetch on interactive shell startup
if [[ $- == *i* ]] && command -v fastfetch >/dev/null 2>&1; then
    fastfetch
fi
