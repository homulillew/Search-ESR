"""Opt-in durable observation runtime; frozen prompts and tool payloads unchanged."""
import hashlib
import json
from .agent import AgentSession, BCPlusTools, TOOLS, AGENT_PROMPT
from .observations import ObservationStore


class ObservedTools(BCPlusTools):
    def __init__(self, store, variant='baseline'):
        super().__init__()
        if variant not in {'baseline','table_entry'}:
            raise ValueError('Unknown window variant')
        self.store,self.variant=store,variant

    def _windows(self):
        if self.window_builder is None and self.variant=='table_entry':
            from transformers import AutoTokenizer
            from .structural_windows import TableEntryWindowBuilder
            self.window_builder=TableEntryWindowBuilder(AutoTokenizer.from_pretrained('/data/model/Qwen3-Embedding-8B',local_files_only=True,use_fast=True))
        return super()._windows()

    def execute(self, name, arguments):
        if name=='open' and isinstance(arguments,dict) and isinstance(arguments.get('window_ref'),str):
            ref=arguments['window_ref']
            if ref not in self.store.seen:
                raise ValueError('Window was not returned in this active session')
            if ref not in self._windows().windows:
                self.store.restore_window(self._windows(),ref)
        result=super().execute(name,arguments)
        if name in {'search','open'}:
            self.store.record(name,arguments,result,self._windows())
        return result


class ObservedAgentSession(AgentSession):
    def __init__(self, config, *, state_path=':memory:', variant=None, client=None,
                 max_rounds=64, on_status=None):
        self.observations=ObservationStore(state_path)
        saved=self.observations.checkpoint()
        variant=variant or (saved['variant'] if saved else 'baseline')
        self.variant=variant
        self.protocol_hash=hashlib.sha256(json.dumps([config.system_prompt,AGENT_PROMPT,TOOLS],ensure_ascii=False).encode()).hexdigest()
        self._initializing=True
        if saved and (saved['variant']!=variant or saved['model']!=config.model or saved['base_url']!=config.base_url or saved['protocol_hash']!=self.protocol_hash):
            self.observations.close()
            raise ValueError('State configuration differs; use a new state file')
        if not saved and self.observations.sequence:
            self.observations.close()
            raise ValueError('Observation-only store has no chat checkpoint; use a new state file')
        super().__init__(config,client=client,tools=ObservedTools(self.observations,variant),max_rounds=max_rounds,on_status=on_status)
        self._initializing=False
        if saved:
            self.observations.deactivate_after(saved['sequence'])
            self.messages=saved['messages']
        else:
            self._save()

    def _save(self):
        self.observations.save_checkpoint(dict(model=self.config.model,base_url=self.config.base_url,
            protocol_hash=self.protocol_hash,variant=self.variant,messages=self.messages))

    def ask(self, text, **kwargs):
        mark=self.observations.sequence
        previous=list(self.messages)
        try:
            answer=super().ask(text,**kwargs)
            self._save()
            return answer
        except BaseException:
            self.messages=previous
            self.observations.deactivate_after(mark)
            raise

    def reset(self):
        super().reset()
        if not getattr(self,'_initializing',True):
            self.observations.deactivate_after(0)
            self._save()

    def close(self):
        try:
            super().close()
        finally:
            self.observations.close()
