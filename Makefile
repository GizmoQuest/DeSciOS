# DeSciOS Launcher Build System
# =============================

.PHONY: all binary package deb clean install uninstall help

# Default target
all: binary package

# Build binary only
binary:
	@echo "🔨 Building DeSciOS Launcher binary..."
	python3 build_launcher.py

# Build binary and package
package: binary
	@echo "📦 Building DeSciOS Launcher package..."
	python3 build_deb.py

# Complete build (binary + package + release info)
release:
	@echo "🚀 Building complete DeSciOS Launcher release..."
	python3 build_all.py

# Build .deb package only (requires existing binary)
deb:
	@echo "📦 Building .deb package..."
	python3 build_deb.py

# Install the binary system-wide (Linux/macOS)
install:
	@echo "📥 Installing DeSciOS Launcher..."
	@if [ -f "descios-launcher_*.deb" ]; then \
		echo "Installing via .deb package..."; \
		sudo dpkg -i descios-launcher_*.deb; \
		sudo apt-get install -f; \
	elif [ -f "dist/descios" ]; then \
		echo "Installing binary manually..."; \
		sudo cp dist/descios /usr/local/bin/; \
		sudo chmod +x /usr/local/bin/descios; \
		echo "✓ DeSciOS Launcher installed to /usr/local/bin/descios"; \
	elif [ -d "dist/descios.app" ]; then \
		echo "Installing macOS app..."; \
		cp -r dist/descios.app /Applications/; \
		echo "✓ DeSciOS Launcher installed to /Applications/descios.app"; \
	else \
		echo "❌ No binary or package found. Run 'make binary' first."; \
		exit 1; \
	fi

# Uninstall the launcher
uninstall:
	@echo "📤 Uninstalling DeSciOS Launcher..."
	@if dpkg -l | grep -q descios-launcher; then \
		echo "Removing via package manager..."; \
		sudo apt remove descios-launcher; \
	elif [ -f "/usr/local/bin/descios" ]; then \
		echo "Removing manual installation..."; \
		sudo rm -f /usr/local/bin/descios; \
		echo "✓ DeSciOS Launcher removed from /usr/local/bin/"; \
	elif [ -d "/Applications/descios.app" ]; then \
		echo "Removing macOS app..."; \
		rm -rf /Applications/descios.app; \
		echo "✓ DeSciOS Launcher removed from /Applications/"; \
	else \
		echo "⚠️  DeSciOS Launcher not found in standard locations"; \
	fi

# Clean build artifacts
clean:
	@echo "🧹 Cleaning build artifacts..."
	rm -rf dist/
	rm -rf build/
	rm -f *.spec
	rm -f *.deb
	rm -f RELEASE_INFO.txt
	@echo "✓ Build artifacts cleaned"

# Install build dependencies
deps:
	@echo "📋 Installing build dependencies..."
	pip3 install pyinstaller
	@if [ "$(shell uname)" = "Linux" ]; then \
		echo "Installing Debian packaging tools..."; \
		sudo apt update; \
		sudo apt install -y dpkg-dev gzip; \
	fi
	@echo "✓ Dependencies installed"

# Run the launcher (for testing)
run:
	@echo "🚀 Running DeSciOS Launcher..."
	@if [ -f "dist/descios" ]; then \
		./dist/descios; \
	elif [ -d "dist/descios.app" ]; then \
		open dist/descios.app; \
	elif [ -f "dist/descios.exe" ]; then \
		./dist/descios.exe; \
	else \
		echo "No binary found. Running from source..."; \
		python3 descios_launcher/main.py; \
	fi

# Show help
help:
	@echo "DeSciOS Launcher Build System"
	@echo "============================"
	@echo ""
	@echo "Available targets:"
	@echo "  all      - Build binary and package (default)"
	@echo "  binary   - Build binary only"
	@echo "  package  - Build binary and package"
	@echo "  release  - Complete build with release info"
	@echo "  deb      - Build .deb package only"
	@echo "  install  - Install launcher system-wide"
	@echo "  uninstall- Remove launcher from system"
	@echo "  clean    - Clean build artifacts"
	@echo "  deps     - Install build dependencies"
	@echo "  run      - Run the launcher (binary or source)"
	@echo "  help     - Show this help message"
	@echo ""
	@echo "Quick start:"
	@echo "  make deps     # Install dependencies"
	@echo "  make release  # Build everything"
	@echo "  make install  # Install system-wide"
	@echo ""
	@echo "Platform-specific binaries created:"
	@echo "  Linux:   dist/descios"
	@echo "  macOS:   dist/descios.app"  
	@echo "  Windows: dist/descios.exe" 