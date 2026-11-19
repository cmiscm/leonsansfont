PYTHON ?= python3
FONTSPECTOR ?= fontspector
QA_DIR ?= output/qa

.PHONY: help build test check proof package release
help:
	@echo 'make build   - compile variable TTF, webfont and development package'
	@echo 'make test    - build and run the unfiltered Google Fonts profile'
	@echo 'make check   - build and run local shaping, spacing and sanitizer checks'
	@echo 'make proof   - build and create a self-contained review specimen'
	@echo 'make release - require a committed source tree and strict QA evidence'
	@echo 'Override PYTHON and FONTSPECTOR to select installed tools.'

build:
	$(PYTHON) scripts/build.py

package:
	$(PYTHON) scripts/prepare_metadata.py

test: build
	$(PYTHON) scripts/qa.py --fontspector "$(FONTSPECTOR)" --output "$(QA_DIR)"
	$(PYTHON) scripts/check_release.py --qa-directory "$(QA_DIR)"

check: build
	$(PYTHON) scripts/check_shaping.py --output "$(QA_DIR)/shaping.json"
	$(PYTHON) scripts/check_mark_clearance.py --output "$(QA_DIR)/mark-clearance.json"
	$(PYTHON) scripts/check_spacing.py --output "$(QA_DIR)/spacing.json"
	$(PYTHON) scripts/check_instances.py --output "$(QA_DIR)/instances.json"

proof: build
	$(PYTHON) scripts/proof.py --output output/proof/index.html

release: test
	$(PYTHON) scripts/prepare_metadata.py --release --qa-directory "$(QA_DIR)"
