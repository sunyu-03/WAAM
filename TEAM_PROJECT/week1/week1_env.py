"""Week 1 environment: team interface with collision-aware terminal success."""
from environment.gym_wrapper import WaamGymEnv


class Week1Env(WaamGymEnv):
    """Keep upstream physics; require no collision in the entire episode."""

    def reset(self, *, seed=None, options=None):
        observation, info = super().reset(seed=seed, options=options)
        self._episode_collision_free = True
        info['episode_collision_free'] = True
        return observation, info

    def step(self, action):
        observation, reward, terminated, truncated, info = super().step(action)
        self._episode_collision_free &= bool(info['collision_pass'])
        info['episode_collision_free'] = self._episode_collision_free
        info['upstream_success'] = info['success']
        if terminated or truncated:
            success = bool(info['success']) and self._episode_collision_free
            final_reward = self.terminal_reward if success else -self.terminal_penalty
            reward += final_reward - info['reward_terminal']
            info['reward_terminal'] = final_reward
            info['success'] = int(success)
        return observation, float(reward), terminated, truncated, info
