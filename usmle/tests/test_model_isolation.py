import importlib.util
import sqlite3
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import pipeline as p


def meta(i, model):
    return dict(execution_id=str(i), copilot_home='home'+str(i), workdir='work'+str(i), model=model)


class ModelIsolationTests(unittest.TestCase):
    def test_distinct_families_required_in_memory(self):
        a, b, c = meta(1,'gpt-5.4'), meta(2,'claude-sonnet-4.6'), meta(3,'claude-sonnet-4.6')
        self.assertTrue(p.isolation_gate(a,b,c))
        for invalid in ['auto', 'gpt-5.4', '', None, 'unknown-model']:
            with self.subTest(model=invalid):
                self.assertFalse(p.isolation_gate(a,dict(b,model=invalid),c))
                self.assertFalse(p.isolation_gate(a,b,dict(c,model=invalid)))

    def test_reused_context_rejected(self):
        a,b,c=meta(1,'gpt-5.4'),meta(2,'claude-sonnet-4.6'),meta(3,'claude-sonnet-4.6')
        for field in ['execution_id','copilot_home','workdir']:
            self.assertFalse(p.isolation_gate(a,dict(b,**{field:a[field]}),c))

    def test_database_gate_matches_memory_gate(self):
        with sqlite3.connect(':memory:') as con:
            con.execute('CREATE TABLE executions(candidate_id,role,execution_id,model,prompt_sha256,context_namespace_sha256)')
            roles=['AUTHOR_EXECUTION','AUDITOR_EXECUTION_PASS_A','AUDITOR_EXECUTION_PASS_B']
            for i,role in enumerate(roles):
                con.execute('INSERT INTO executions VALUES(?,?,?,?,?,?)',('candidate',role,str(i),'gpt-5.4' if i==0 else 'claude-sonnet-4.6','prompt'+str(i),'context'+str(i)))
            self.assertTrue(p.isolation_gate_db(con,'candidate'))
            for invalid in ['auto','gpt-5.4','unknown-model']:
                con.execute("UPDATE executions SET model=? WHERE role='AUDITOR_EXECUTION_PASS_B'",(invalid,))
                self.assertFalse(p.isolation_gate_db(con,'candidate'))

    def test_runner_preserves_gates_and_explicit_model(self):
        # runner intentionally patches pipeline at import; restore globals afterward.
        old={k:getattr(p,k) for k in ['ROOT','DB','STATE','RUN_DIR','run_copilot']}
        original_run=p.subprocess.run
        try:
            spec=importlib.util.spec_from_file_location('isolation_test_runner',ROOT/'runner.py')
            runner=importlib.util.module_from_spec(spec);spec.loader.exec_module(runner)
            self.assertIs(runner._isolation_gate,p.isolation_gate)
            self.assertIs(runner._isolation_gate_db,p.isolation_gate_db)
            with patch.object(runner,'_real_run') as run:
                with self.assertRaises(ValueError): runner._fresh_execution('p','auto','author','id')
                run.assert_not_called()
                run.return_value.returncode=0;run.return_value.stdout='{}'
                _,record=runner._fresh_execution('p','gpt-5.4','author','id')
                cmd=run.call_args.args[0]
                self.assertEqual(cmd[cmd.index('--model')+1],'gpt-5.4')
                self.assertEqual(record['model'],'gpt-5.4')
        finally:
            p.subprocess.run=original_run
            for k,v in old.items():setattr(p,k,v)

if __name__=='__main__':unittest.main()
