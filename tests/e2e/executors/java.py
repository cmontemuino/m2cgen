import os
import subprocess
import shutil

from m2cgen import exporters
from tests.e2e.executors import base


class JavaExecutor(base.BaseExecutor):

    def __init__(self, model):
        self.model = model
        self.exporter = exporters.JavaExporter(model)

        java_home = os.environ.get("JAVA_HOME")
        assert java_home, "JAVA_HOME is not specified"
        self._java_bin = os.path.join(java_home, "bin/java")
        self._javac_bin = os.path.join(java_home, "bin/javac")

    def predict(self, X):

        exec_args = [
            self._java_bin, "-cp", self._resource_tmp_dir,
            "Executor", "Model", "score"
        ]
        exec_args.extend(map(str, X))
        result = subprocess.run(exec_args, stdout=subprocess.PIPE)

        return float(result.stdout)

    def prepare(self):
        # Create files generated by exporter in the temp dir.
        files_to_compile = []
        for model_name, code in self.exporter.export():
            file_name = os.path.join(self._resource_tmp_dir,
                                     "{}.java".format(model_name))

            with open(file_name, "w") as f:
                f.write(code)

            files_to_compile.append(file_name)

        # Move Executor.java to the same temp dir.
        module_path = os.path.dirname(__file__)
        shutil.copy(os.path.join(module_path, "Executor.java"),
                    self._resource_tmp_dir)

        # Compile all files together.
        subprocess.run([self._javac_bin] + files_to_compile + (
            [os.path.join(self._resource_tmp_dir, "Executor.java")]))
