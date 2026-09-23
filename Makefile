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

.DEFAULT_GOAL := help
.PHONY: help qm collab diagrams generate validate check

help:
	@echo "qm        Generate C++ from the QM model"
	@echo "collab    Generate collaboration artifacts"
	@echo "diagrams  Render the collaboration SVG"
	@echo "generate  Run QM, Collab and PlantUML"
	@echo "validate  Read-only model consistency checks"
	@echo "check     Read-only Collab syntax and architecture checks"

qm:
	$(QM) $(QM_MODEL) -c

collab:
	$(PYTHON) $(COLLAB) $(COLLAB_MODEL) -o $(MODEL_DIR)

diagrams:
	$(PLANTUML) -tsvg $(PUML)

generate: qm collab diagrams

validate:
	$(PYTHON) tools/validate_architecture.py $(COLLAB_MODEL) $(QM_MODEL)

check:
	$(PYTHON) $(COLLAB) --check $(COLLAB_MODEL)
	$(MAKE) validate
