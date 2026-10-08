"""Guard against accidentally training the incompatible attachment environment."""
raise SystemExit('PPO integration is blocked: WAAMBaselineEnv is not supplied. The continuous WaamGymEnv and discrete task allocation/checkpoint contracts must be reconciled before training. Use run_pipeline.py for validated greedy scheduling.')
