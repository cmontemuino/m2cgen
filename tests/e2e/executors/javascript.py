import os
from py_mini_racer import py_mini_racer
import m2cgen as m2c
from tests.e2e.executors import base


class JavascriptExecutor(base.BaseExecutor):

    def __init__(self, model):
        self.model = model

    def predict(self, X):
        file_name = os.path.join(self._resource_tmp_dir, "model.js")

        with open(file_name, 'r') as myfile:
            code = myfile.read()

        caller = "score([" + ",".join(map(str, X)) + "]);\n"

        ctx = py_mini_racer.MiniRacer()
        result = ctx.eval(caller + code)

        return result

    def prepare(self):
        code = m2c.export_to_javascript(self.model)

        file_name = os.path.join(self._resource_tmp_dir, "model.js")

        with open(file_name, "w") as f:
            f.write(code)
