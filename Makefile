# Makefile for ARP Spoofing & DNS MitM Assignment
# DAT 505 - Network Security

.PHONY: help install test clean demo setup evidence report all

# Default target
help:
	@echo "🎯 ARP Spoofing & DNS MitM Assignment - DAT 505"
	@echo "=============================================="
	@echo ""
	@echo "Available targets:"
	@echo "  install    - Install Python dependencies"
	@echo "  test       - Run test suite to validate setup"
	@echo "  setup      - Set up lab environment (requires sudo)"
	@echo "  demo       - Run interactive demonstration"
	@echo "  evidence   - Collect evidence files"
	@echo "  clean      - Clean up generated files"
	@echo "  report     - Generate PDF report from template"
	@echo "  all        - Install, test, and prepare for demo"
	@echo ""
	@echo "Quick commands:"
	@echo "  make install test    - Set up and validate environment"
	@echo "  make demo           - Run full demonstration"
	@echo "  make evidence       - Collect all evidence files"

# Install Python dependencies
install:
	@echo "📦 Installing Python dependencies..."
	pip3 install -r requirements.txt
	@echo "✅ Dependencies installed"

# Run test suite
test:
	@echo "🧪 Running test suite..."
	python3 test_suite.py
	@echo "📊 Test complete"

# Quick validation
test-quick:
	@echo "⚡ Running quick validation..."
	python3 test_suite.py --quick

# Set up lab environment (requires sudo)
setup:
	@echo "🔧 Setting up lab environment..."
	@if [ "$$EUID" -ne 0 ]; then \
		echo "❌ This target requires sudo privileges"; \
		echo "   Run: sudo make setup"; \
		exit 1; \
	fi
	chmod +x scripts/*.py
	chmod +x *.py
	chmod +x setup_lab.sh
	mkdir -p pcap_files evidence logs
	@echo "✅ Lab environment ready"

# Run interactive demonstration
demo:
	@echo "🎭 Starting interactive demonstration..."
	@if [ "$$EUID" -ne 0 ]; then \
		echo "❌ Demo requires sudo privileges"; \
		echo "   Run: sudo make demo"; \
		exit 1; \
	fi
	python3 demo.py

# Collect evidence files
evidence:
	@echo "📸 Collecting evidence files..."
	mkdir -p evidence/pcaps evidence/logs evidence/screenshots evidence/configs
	@if [ -d "pcap_files" ] && [ "$(shell ls -A pcap_files 2>/dev/null)" ]; then \
		cp pcap_files/*.pcap evidence/pcaps/ 2>/dev/null || true; \
		echo "  📁 PCAP files copied"; \
	fi
	@if ls *.json >/dev/null 2>&1; then \
		cp *.json evidence/logs/ 2>/dev/null || true; \
		echo "  📄 Log files copied"; \
	fi
	cp config/*.json evidence/configs/ 2>/dev/null || true
	@echo "  📋 Config files copied"
	@echo "✅ Evidence collection complete"
	@echo "📂 Evidence organized in evidence/ directory"

# Generate report
report:
	@echo "📝 Generating report..."
	@if command -v pandoc >/dev/null 2>&1; then \
		pandoc report_template.md -o evidence/report.pdf; \
		echo "✅ PDF report generated: evidence/report.pdf"; \
	else \
		echo "⚠️  pandoc not found - keeping markdown format"; \
		cp report_template.md evidence/report.md; \
		echo "✅ Report template copied: evidence/report.md"; \
	fi

# Clean up generated files
clean:
	@echo "🧹 Cleaning up generated files..."
	rm -rf pcap_files/*.pcap 2>/dev/null || true
	rm -rf *.json 2>/dev/null || true
	rm -rf __pycache__ scripts/__pycache__ 2>/dev/null || true
	rm -rf *.pyc scripts/*.pyc 2>/dev/null || true
	rm -rf logs/* 2>/dev/null || true
	@echo "✅ Cleanup complete"

# Clean everything including evidence
clean-all: clean
	@echo "🗑️  Removing all generated content..."
	rm -rf evidence/* 2>/dev/null || true
	@echo "✅ Full cleanup complete"

# Prepare for submission
prepare-submission: clean evidence report
	@echo "📦 Preparing submission package..."
	mkdir -p submission
	cp -r scripts config evidence submission/
	cp README.md QUICK_START.md requirements.txt submission/
	cp demo.py test_suite.py submission/
	@echo "✅ Submission package ready in submission/"

# Full setup and validation
all: install test setup
	@echo "🎉 Project setup complete!"
	@echo ""
	@echo "Next steps:"
	@echo "  1. sudo make demo    - Run demonstration"
	@echo "  2. make evidence     - Collect evidence"
	@echo "  3. make report       - Generate report"

# Development helpers
lint:
	@echo "🔍 Running code quality checks..."
	@if command -v flake8 >/dev/null 2>&1; then \
		flake8 scripts/*.py *.py --max-line-length=100; \
	else \
		echo "⚠️  flake8 not installed - skipping lint"; \
	fi

# Check dependencies
check-deps:
	@echo "🔍 Checking system dependencies..."
	@echo "Python version: $$(python3 --version)"
	@echo "Pip version: $$(pip3 --version)"
	@echo "Available network interfaces:"
	@ip addr show 2>/dev/null | grep "^[0-9]" | cut -d: -f2 | tr -d ' ' || \
	 ifconfig 2>/dev/null | grep "^[a-z]" | cut -d: -f1 || \
	 echo "  Unable to detect interfaces"

# Show project status
status:
	@echo "📊 Project Status"
	@echo "=================="
	@echo "Python scripts: $$(find scripts -name "*.py" | wc -l)"
	@echo "Config files: $$(find config -name "*.json" | wc -l)"
	@echo "PCAP files: $$(find pcap_files -name "*.pcap" 2>/dev/null | wc -l)"
	@echo "Evidence files: $$(find evidence -type f 2>/dev/null | wc -l)"
	@echo ""
	@echo "Recent activity:"
	@ls -lt | head -5

# Network interface detection helper
show-interfaces:
	@echo "🌐 Available Network Interfaces:"
	@ip addr show 2>/dev/null | grep -E "^[0-9]+:" | sed 's/^[0-9]*: /  /' || \
	 ifconfig 2>/dev/null | grep -E "^[a-z]" | sed 's/:.*//' | sed 's/^/  /' || \
	 echo "  Unable to detect interfaces - check manually"

# Quick security check
security-check:
	@echo "🔒 Security Check"
	@echo "=================="
	@echo "Running as: $$(whoami)"
	@echo "Current directory: $$(pwd)"
	@if [ "$$(pwd)" = "/Users/"* ] || [ "$$(pwd)" = "/home/"* ]; then \
		echo "✅ Running in user directory"; \
	else \
		echo "⚠️  Not in user directory - verify location"; \
	fi
	@if [ -f "config/dns_targets.json" ]; then \
		echo "✅ DNS config found"; \
	else \
		echo "❌ DNS config missing"; \
	fi
