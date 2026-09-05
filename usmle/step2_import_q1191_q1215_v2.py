#!/usr/bin/env python3
import importlib.util, pathlib

HERE=pathlib.Path(__file__).resolve().parent
TARGET=HERE/'step2_import_q1191_q1215.py'
spec=importlib.util.spec_from_file_location('q1191_q1215_strict',TARGET)
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
mod.EXPECTED_COMPETENCIES={
 'Medical Knowledge: Applying Foundational Science Concepts':821,
 'Patient Care: Diagnosis, including history and physical examination':243,
 'Practice-Based Learning and Improvement':66,
 'Communication and Interpersonal Skills':85,
}
mod.main()
