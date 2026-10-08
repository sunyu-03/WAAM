"""Guard against accidentally training the incompatible attachment environment."""
raise SystemExit('WAAMBaselineEnv is implemented. PPO training remains blocked: the task-count-dependent observation differs from the preserved 13-value checkpoint, and the continuous wrapper has different action semantics. Use run_pipeline.py for validated greedy scheduling.')
