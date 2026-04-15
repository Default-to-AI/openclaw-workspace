#!/usr/bin/env bash
# --------------------------------------------------------------------------
# BLE.SH / Terminal Color Formatting Guide
# --------------------------------------------------------------------------

# Print title
echo -e "\n\033[1;35m🎨 BLE.SH TERMINAL COLOR & FORMATTING GUIDE\033[0m"
echo -e "\033[90m──────────────────────────────────────────────────────────────────────\033[0m"
echo -e "Usage in ~/.blerc: \033[1;36mble-face -s <category> \"fg=<color>,bg=<color>,<modifier>\"\033[0m\n"

# 1. 16 STANDARD COLORS
echo -e "\033[1;33m1. STANDARD NAMED COLORS (0-15)\033[0m"
echo -e "You can use standard names like 'red' or 'blue'\n"

colors=("black" "red" "green" "yellow" "blue" "magenta" "cyan" "white")
for i in {0..7}; do
    printf "\033[38;5;%sm %-10s \033[0m" "$i" "${colors[$i]}"
done
echo
for i in {8..15}; do
    name="bright_${colors[$i-8]}"
    if [ "$name" == "bright_black" ]; then name="gray"; fi
    printf "\033[38;5;%sm %-10s \033[0m" "$i" "$name"
done
echo -e "\n\n"

# 2. 256 EXTENDED COLORS
echo -e "\033[1;33m2. 256 EXTENDED COLORS (0-255)\033[0m"
echo -e "Use the number in ~/.blerc like: \033[38;5;213m\"fg=213\"\033[0m or \033[48;5;27m\"bg=27\"\033[0m\n"

for i in {16..255}; do
    # Print the color block and number
    printf "\033[38;5;%sm %3s \033[0m" "$i" "$i"
    
    # Line breaks to make a neat block
    if (( (i - 15) % 6 == 0 )); then
        echo -n "  "
    fi
    if (( (i - 15) % 36 == 0 )); then
        echo
    fi
done
echo -e "\n"

# 3. MODIFIERS
echo -e "\033[1;33m3. TEXT MODIFIERS\033[0m"
echo -e "Combine these separated by commas, e.g., \033[1;3;4;36m\"fg=cyan,bold,italic,underline\"\033[0m\n"

echo -e "  \033[1m bold       \033[0m : \"bold\""
echo -e "  \033[2m dim        \033[0m : \"dim\" (faint)"
echo -e "  \033[3m italic     \033[0m : \"italic\""
echo -e "  \033[4m underline  \033[0m : \"underline\""
echo -e "  \033[7m reverse    \033[0m : \"reverse\" (swaps fg/bg)"
echo -e "  \033[9m strike     \033[0m : \"strike\""
echo -e "\n"

# 4. BLE.SH CATEGORY EXAMPLES
echo -e "\033[1;33m4. COMMON CATEGORIES TO CHANGE IN ~/.blerc\033[0m\n"

echo -e "  \033[1;36mble-face command_builtin=\"fg=blue,bold\"\033[0m"
echo -e "      Effect: Highlights built-ins like \033[1;34mcd\033[0m or \033[1;34mecho\033[0m\n"

echo -e "  \033[1;36mble-face command_alias=\"fg=cyan\"\033[0m"
echo -e "      Effect: Highlights your aliases like \033[0;36mll\033[0m or \033[0;36mla\033[0m\n"

echo -e "  \033[1;36mble-face command_function=\"fg=green\"\033[0m"
echo -e "      Effect: Highlights functions like \033[0;32msfind\033[0m or \033[0;32mtodo\033[0m\n"

echo -e "  \033[1;36mble-face command_file=\"fg=blue\"\033[0m"
echo -e "      Effect: Identifies valid installed commands like \033[0;34mgrep\033[0m or \033[0;34mpython\033[0m\n"

echo -e "  \033[1;36mble-face syntax_error=\"fg=167,italic\"\033[0m"
echo -e "      Effect: Invalid commands or missing quotes: \033[3;38;5;167mcommander\033[0m\n"

echo -e "  \033[1;36mble-face argument_option=\"fg=214\"\033[0m"
echo -e "      Effect: Command flags like \033[38;5;214m--help\033[0m or \033[38;5;214m-al\033[0m\n"

echo -e "  \033[1;36mble-face argument_error=\"fg=167,italic\"\033[0m"
echo -e "      Effect: Unrecognized flags or arguments: \033[3;38;5;167m--nonexistent-flag\033[0m\n"

echo -e "  \033[1;36mble-face filename_directory=\"fg=blue,underline\"\033[0m"
echo -e "      Effect: Valid folder paths like \033[4;34m~/.openclaw\033[0m\n"

echo -e "  \033[1;36mble-face auto_complete=\"fg=239,italic\"\033[0m"
echo -e "      Effect: Ghost text recommendations like \033[3;38;5;239mhistory_command_here\033[0m\n"

echo -e "\033[90m──────────────────────────────────────────────────────────────────────\033[0m"
echo -e "\033[32m✔ Script execution complete. Open \033[1;37m~/.blerc\033[0m \033[32mto make adjustments.\033[0m\n"
