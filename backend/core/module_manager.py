# ============================================================
# KJs TRD Trading Terminal - Module Manager
# ============================================================

import os
import sys
import importlib
from datetime import datetime

class ModuleManager:
    """Manages all modules in the platform."""

    def __init__(self):
        self.modules = {}
        self.module_metadata = {}
        self.module_directory = 'modules/'
        self.runtime_engine = None

    def initialize(self, runtime_engine=None):
        """Initialize the module manager."""
        self.runtime_engine = runtime_engine
        self._log("INFO", "Module Manager initialized")
        return True

    def discover_modules(self):
        """Discover all modules in the modules directory."""
        discovered = []

        if not os.path.exists(self.module_directory):
            os.makedirs(self.module_directory)
            self._log("INFO", f"Created modules directory: {self.module_directory}")
            return discovered

        for root, dirs, files in os.walk(self.module_directory):
            for file in files:
                if file.endswith('.py') and not file.startswith('__'):
                    module_path = os.path.join(root, file)
                    module_name = os.path.splitext(file)[0]
                    module_type = os.path.basename(root)

                    discovered.append({
                        'name': module_name,
                        'path': module_path,
                        'type': module_type,
                        'file': file
                    })

        self._log("INFO", f"Discovered {len(discovered)} modules")
        return discovered

    def load_module(self, module_name, module_path):
        """Load a specific module."""
        try:
            module_dir = os.path.dirname(module_path)
            if module_dir not in sys.path:
                sys.path.append(module_dir)

            module_name_only = os.path.splitext(os.path.basename(module_path))[0]
            module = importlib.import_module(module_name_only)

            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if callable(attr) and not attr_name.startswith('_'):
                    if hasattr(attr, 'name') and hasattr(attr, 'type'):
                        instance = attr()
                        instance.module_path = module_path
                        instance.module_name = module_name

                        self.modules[module_name] = instance
                        self.module_metadata[module_name] = {
                            'name': instance.name,
                            'type': instance.type,
                            'version': getattr(instance, 'version', '1.0.0'),
                            'author': getattr(instance, 'author', 'Unknown'),
                            'description': getattr(instance, 'description', ''),
                            'path': module_path,
                            'status': 'loaded',
                            'loaded_at': datetime.now().isoformat()
                        }

                        self._log("INFO", f"Loaded module: {module_name} ({instance.type})")
                        return instance

            self._log("ERROR", f"No valid module class found in {module_path}")
            return None

        except Exception as e:
            self._log("ERROR", f"Failed to load module {module_name}: {str(e)}")
            return None

    def load_all_modules(self):
        """Load all discovered modules."""
        discovered = self.discover_modules()
        loaded = []

        for module_info in discovered:
            instance = self.load_module(module_info['name'], module_info['path'])
            if instance:
                loaded.append(module_info['name'])

        self._log("INFO", f"Loaded {len(loaded)} modules")
        return loaded

    def unload_module(self, module_name):
        """Unload a module."""
        if module_name in self.modules:
            if self.runtime_engine:
                self.runtime_engine.stop_module(module_name)

            del self.modules[module_name]
            if module_name in self.module_metadata:
                self.module_metadata[module_name]['status'] = 'unloaded'
            self._log("INFO", f"Unloaded module: {module_name}")
            return True
        return False

    def get_module(self, module_name):
        """Get a module instance."""
        return self.modules.get(module_name)

    def get_all_modules(self):
        """Get all loaded modules."""
        return list(self.modules.keys())

    def get_module_metadata(self, module_name):
        """Get metadata for a module."""
        return self.module_metadata.get(module_name)

    def get_all_metadata(self):
        """Get metadata for all modules."""
        return self.module_metadata

    def get_modules_by_type(self, module_type):
        """Get all modules of a specific type."""
        result = []
        for name, meta in self.module_metadata.items():
            if meta.get('type') == module_type:
                result.append(name)
        return result

    def reload_module(self, module_name):
        """Reload a module."""
        if module_name in self.modules:
            module_info = self.module_metadata.get(module_name)
            if module_info:
                path = module_info.get('path')
                if path:
                    self.unload_module(module_name)
                    return self.load_module(module_name, path)
        return None

    def create_module(self, module_name, module_type, code):
        """Create a new module."""
        module_dir = os.path.join(self.module_directory, module_type)
        os.makedirs(module_dir, exist_ok=True)

        module_path = os.path.join(module_dir, f"{module_name}.py")

        with open(module_path, 'w') as f:
            f.write(code)

        self._log("INFO", f"Created module: {module_name}.py in {module_type}/")
        return self.load_module(module_name, module_path)

    def delete_module(self, module_name):
        """Delete a module."""
        if module_name in self.module_metadata:
            path = self.module_metadata[module_name].get('path')
            if path and os.path.exists(path):
                self.unload_module(module_name)
                os.remove(path)
                self._log("INFO", f"Deleted module: {module_name}")
                return True
        return False

    def _log(self, level, message):
        """Log a message."""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] [ModuleManager] [{level}] {message}")
