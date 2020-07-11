import os

import environ


ROOT = environ.Path(__file__) - 2

env_file = os.path.join(ROOT, '.env')


env = environ.Env()
environ.Env.read_env(env_file)
