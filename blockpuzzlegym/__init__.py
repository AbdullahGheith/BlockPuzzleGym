from gym.envs.registration import register

register(
    id='BlockPuzzleGym-v0',
    entry_point='blockpuzzlegym.envs.BlockPuzzleGym:BlockPuzzleGym',
)