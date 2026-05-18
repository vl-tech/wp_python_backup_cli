.PHONY: install dev autocomplete all

all: install
	@echo ""
	@$(MAKE) autocomplete

install:
	@echo "=== Installing system dependencies ==="
	apt install -y python3-paramiko python3-argcomplete python3-cryptography
	chmod +x wp_backup.py
	@echo "Done. wp_backup.py is ready to use."
	@echo ""
	@$(MAKE) autocomplete

dev:
	@echo "=== Installing as editable package ==="
	pip install -e . --break-system-packages
	@echo "Done. Run 'wp_backup --help' from anywhere."
	@echo ""
	@$(MAKE) autocomplete-dev

autocomplete:
	@echo ""
	@echo "=== Autocomplete Setup ==="
	@echo "  1) Global - activate for all argcomplete scripts (requires sudo)"
	@echo "  2) This script only - adds to ~/.bashrc"
	@echo "  3) Skip"
	@read -p "Choose [1/2/3]: " choice; \
	case "$$choice" in \
		1) \
			sudo activate-global-python-argcomplete && \
			echo "Global autocomplete activated. Run: source ~/.bashrc" ;; \
		2) \
			if grep -qF "register-python-argcomplete wp_backup.py" ~/.bashrc 2>/dev/null; then \
				echo "Autocomplete already configured in ~/.bashrc"; \
			else \
				{ register-python-argcomplete wp_backup.py; \
				  printf 'complete -o nospace -o default -o bashdefault -F _python_argcomplete ./wp_backup.py\n'; \
				} >> ~/.bashrc && \
				echo "Added to ~/.bashrc. Run: source ~/.bashrc to activate."; \
			fi ;; \
		3) echo "Skipped." ;; \
		*) echo "Invalid choice, skipped." ;; \
	esac

autocomplete-dev:
	@echo ""
	@echo "=== Autocomplete Setup (installed command) ==="
	@echo "  1) Global - activate for all argcomplete scripts (requires sudo)"
	@echo "  2) wp_backup command only - adds to ~/.bashrc"
	@echo "  3) Skip"
	@read -p "Choose [1/2/3]: " choice; \
	case "$$choice" in \
		1) \
			sudo activate-global-python-argcomplete && \
			echo "Global autocomplete activated. Run: source ~/.bashrc" ;; \
		2) \
			if grep -qF "register-python-argcomplete wp_backup" ~/.bashrc 2>/dev/null; then \
				echo "Autocomplete already configured in ~/.bashrc"; \
			else \
				register-python-argcomplete wp_backup >> ~/.bashrc && \
				echo "Added to ~/.bashrc. Run: source ~/.bashrc to activate."; \
			fi ;; \
		3) echo "Skipped." ;; \
		*) echo "Invalid choice, skipped." ;; \
	esac
