import os
from flask_assets import Environment, Bundle
assets = Environment()

css = Bundle(os.getenv('CSS'))
assets.register('css_min', css)

favicon = Bundle('favicon.js')
assets.register('favicon', favicon)

js = Bundle(os.getenv('JS'))
assets.register('scripts', js)
