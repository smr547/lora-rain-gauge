# Rain gauge model-generation and architecture-check workflow.
# Override tool locations on the command line or in the environment.
PYTHON ?= python3
QM ?= ./tools/qm
COLLAB ?= ../collab/src/collabc.py
PLANTUML ?= plantuml
MODEL_DIR := rain-gauge-node/model
QM_MODEL := $(MODEL_DIR)/model.qm
COLLAB_MODEL := $(MODEL_DIR)/rain-gauge.collab
PUML := $(MODEL_DIR)/rain-gauge.puml
QS_DICT_GENERATOR := tools/generate_qs_dict.py
QS_DICT := $(MODEL_DIR)/generated/qs_dict.inc

.DEFAULT_GOAL := help
.PHONY: help qm qs-dict collab diagrams generate validate test check

help:
	@echo "qm        Generate C++ from the QM model"
	@echo "qs-dict   Generate QSPY signal and AO dictionaries"
	@echo "collab    Generate collaboration artifacts"
	@echo "diagrams  Render the collaboration SVG"
	@echo "generate  Run QM, QSPY dictionary, Collab and PlantUML"
	@echo "validate  Read-only model consistency checks"
	@echo "test      Run validator regression tests"
	@echo "check     Read-only Collab, architecture and regression checks"

qm:
	$(QM) $(QM_MODEL) -c

qs-dict: qm
	$(PYTHON) $(QS_DICT_GENERATOR) $(QM_MODEL) -o $(QS_DICT) --no-guard

collab:
	$(PYTHON) $(COLLAB) $(COLLAB_MODEL) -o $(MODEL_DIR)

diagrams:
	$(PLANTUML) -tsvg $(PUML)

generate: qs-dict collab diagrams

validate:
	$(PYTHON) tools/validate_architecture.py $(COLLAB_MODEL) $(QM_MODEL)

test:
	$(PYTHON) -m unittest discover -s tests -v

check:
	$(PYTHON) $(COLLAB) --check $(COLLAB_MODEL)
	$(MAKE) validate
	$(MAKE) test
