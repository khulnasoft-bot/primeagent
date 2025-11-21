"""Primeagent backwards compatibility layer.

This module provides backwards compatibility by forwarding imports from
primeagent.* to wfx.* to maintain compatibility with existing code that
references the old primeagent module structure.
"""

import importlib
import importlib.util
import sys
from types import ModuleType
from typing import Any


class PrimeagentCompatibilityModule(ModuleType):
    """A module that forwards attribute access to the corresponding wfx module."""

    def __init__(self, name: str, wfx_module_name: str):
        super().__init__(name)
        self._wfx_module_name = wfx_module_name
        self._wfx_module = None

    def _get_wfx_module(self):
        """Lazily import and cache the wfx module."""
        if self._wfx_module is None:
            try:
                self._wfx_module = importlib.import_module(self._wfx_module_name)
            except ImportError as e:
                msg = f"Cannot import {self._wfx_module_name} for backwards compatibility with {self.__name__}"
                raise ImportError(msg) from e
        return self._wfx_module

    def __getattr__(self, name: str) -> Any:
        """Forward attribute access to the wfx module with caching."""
        wfx_module = self._get_wfx_module()
        try:
            attr = getattr(wfx_module, name)
        except AttributeError as e:
            msg = f"module '{self.__name__}' has no attribute '{name}'"
            raise AttributeError(msg) from e
        else:
            # Cache the attribute in our __dict__ for faster subsequent access
            setattr(self, name, attr)
            return attr

    def __dir__(self):
        """Return directory of the wfx module."""
        try:
            wfx_module = self._get_wfx_module()
            return dir(wfx_module)
        except ImportError:
            return []


def _setup_compatibility_modules():
    """Set up comprehensive compatibility modules for primeagent.base imports."""
    # First, set up the base attribute on this module (primeagent)
    current_module = sys.modules[__name__]

    # Define all the modules we need to support
    module_mappings = {
        # Core base module
        "primeagent.base": "wfx.base",
        # Inputs module - critical for class identity
        "primeagent.inputs": "wfx.inputs",
        "primeagent.inputs.inputs": "wfx.inputs.inputs",
        # Schema modules - also critical for class identity
        "primeagent.schema": "wfx.schema",
        "primeagent.schema.data": "wfx.schema.data",
        "primeagent.schema.serialize": "wfx.schema.serialize",
        # Template modules
        "primeagent.template": "wfx.template",
        "primeagent.template.field": "wfx.template.field",
        "primeagent.template.field.base": "wfx.template.field.base",
        # Components modules
        "primeagent.components": "wfx.components",
        "primeagent.components.helpers": "wfx.components.helpers",
        "primeagent.components.helpers.calculator_core": "wfx.components.helpers.calculator_core",
        "primeagent.components.helpers.create_list": "wfx.components.helpers.create_list",
        "primeagent.components.helpers.current_date": "wfx.components.helpers.current_date",
        "primeagent.components.helpers.id_generator": "wfx.components.helpers.id_generator",
        "primeagent.components.helpers.memory": "wfx.components.helpers.memory",
        "primeagent.components.helpers.output_parser": "wfx.components.helpers.output_parser",
        "primeagent.components.helpers.store_message": "wfx.components.helpers.store_message",
        # Individual modules that exist in wfx
        "primeagent.base.agents": "wfx.base.agents",
        "primeagent.base.chains": "wfx.base.chains",
        "primeagent.base.data": "wfx.base.data",
        "primeagent.base.data.utils": "wfx.base.data.utils",
        "primeagent.base.document_transformers": "wfx.base.document_transformers",
        "primeagent.base.embeddings": "wfx.base.embeddings",
        "primeagent.base.flow_processing": "wfx.base.flow_processing",
        "primeagent.base.io": "wfx.base.io",
        "primeagent.base.io.chat": "wfx.base.io.chat",
        "primeagent.base.io.text": "wfx.base.io.text",
        "primeagent.base.langchain_utilities": "wfx.base.langchain_utilities",
        "primeagent.base.memory": "wfx.base.memory",
        "primeagent.base.models": "wfx.base.models",
        "primeagent.base.models.google_generative_ai_constants": "wfx.base.models.google_generative_ai_constants",
        "primeagent.base.models.openai_constants": "wfx.base.models.openai_constants",
        "primeagent.base.models.anthropic_constants": "wfx.base.models.anthropic_constants",
        "primeagent.base.models.aiml_constants": "wfx.base.models.aiml_constants",
        "primeagent.base.models.aws_constants": "wfx.base.models.aws_constants",
        "primeagent.base.models.groq_constants": "wfx.base.models.groq_constants",
        "primeagent.base.models.novita_constants": "wfx.base.models.novita_constants",
        "primeagent.base.models.ollama_constants": "wfx.base.models.ollama_constants",
        "primeagent.base.models.sambanova_constants": "wfx.base.models.sambanova_constants",
        "primeagent.base.models.cometapi_constants": "wfx.base.models.cometapi_constants",
        "primeagent.base.prompts": "wfx.base.prompts",
        "primeagent.base.prompts.api_utils": "wfx.base.prompts.api_utils",
        "primeagent.base.prompts.utils": "wfx.base.prompts.utils",
        "primeagent.base.textsplitters": "wfx.base.textsplitters",
        "primeagent.base.tools": "wfx.base.tools",
        "primeagent.base.vectorstores": "wfx.base.vectorstores",
    }

    # Create compatibility modules for each mapping
    for primeagent_name, wfx_name in module_mappings.items():
        if primeagent_name not in sys.modules:
            # Check if the wfx module exists
            try:
                spec = importlib.util.find_spec(wfx_name)
                if spec is not None:
                    # Create compatibility module
                    compat_module = PrimeagentCompatibilityModule(primeagent_name, wfx_name)
                    sys.modules[primeagent_name] = compat_module

                    # Set up the module hierarchy
                    parts = primeagent_name.split(".")
                    if len(parts) > 1:
                        parent_name = ".".join(parts[:-1])
                        parent_module = sys.modules.get(parent_name)
                        if parent_module is not None:
                            setattr(parent_module, parts[-1], compat_module)

                    # Special handling for top-level modules
                    if primeagent_name == "primeagent.base":
                        current_module.base = compat_module
                    elif primeagent_name == "primeagent.inputs":
                        current_module.inputs = compat_module
                    elif primeagent_name == "primeagent.schema":
                        current_module.schema = compat_module
                    elif primeagent_name == "primeagent.template":
                        current_module.template = compat_module
                    elif primeagent_name == "primeagent.components":
                        current_module.components = compat_module
            except (ImportError, ValueError):
                # Skip modules that don't exist in wfx
                continue

    # Handle modules that exist only in primeagent (like knowledge_bases)
    # These need special handling because they're not in wfx yet
    primeagent_only_modules = {
        "primeagent.base.data.kb_utils": "primeagent.base.data.kb_utils",
        "primeagent.base.knowledge_bases": "primeagent.base.knowledge_bases",
        "primeagent.components.knowledge_bases": "primeagent.components.knowledge_bases",
    }

    for primeagent_name in primeagent_only_modules:
        if primeagent_name not in sys.modules:
            try:
                # Try to find the actual physical module file
                from pathlib import Path

                base_dir = Path(__file__).parent

                if primeagent_name == "primeagent.base.data.kb_utils":
                    kb_utils_file = base_dir / "base" / "data" / "kb_utils.py"
                    if kb_utils_file.exists():
                        spec = importlib.util.spec_from_file_location(primeagent_name, kb_utils_file)
                        if spec is not None and spec.loader is not None:
                            module = importlib.util.module_from_spec(spec)
                            sys.modules[primeagent_name] = module
                            spec.loader.exec_module(module)

                            # Also add to parent module
                            parent_module = sys.modules.get("primeagent.base.data")
                            if parent_module is not None:
                                parent_module.kb_utils = module

                elif primeagent_name == "primeagent.base.knowledge_bases":
                    kb_dir = base_dir / "base" / "knowledge_bases"
                    kb_init_file = kb_dir / "__init__.py"
                    if kb_init_file.exists():
                        spec = importlib.util.spec_from_file_location(primeagent_name, kb_init_file)
                        if spec is not None and spec.loader is not None:
                            module = importlib.util.module_from_spec(spec)
                            sys.modules[primeagent_name] = module
                            spec.loader.exec_module(module)

                            # Also add to parent module
                            parent_module = sys.modules.get("primeagent.base")
                            if parent_module is not None:
                                parent_module.knowledge_bases = module

                elif primeagent_name == "primeagent.components.knowledge_bases":
                    components_kb_dir = base_dir / "components" / "knowledge_bases"
                    components_kb_init_file = components_kb_dir / "__init__.py"
                    if components_kb_init_file.exists():
                        spec = importlib.util.spec_from_file_location(primeagent_name, components_kb_init_file)
                        if spec is not None and spec.loader is not None:
                            module = importlib.util.module_from_spec(spec)
                            sys.modules[primeagent_name] = module
                            spec.loader.exec_module(module)

                            # Also add to parent module
                            parent_module = sys.modules.get("primeagent.components")
                            if parent_module is not None:
                                parent_module.knowledge_bases = module
            except (ImportError, AttributeError):
                # If direct file loading fails, skip silently
                continue


# Set up all the compatibility modules
_setup_compatibility_modules()
