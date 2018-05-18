from flask_assets import Environment, Bundle
assets = Environment()

css = Bundle('style.css', output='style.css')
assets.register('css_min', css)

favicon = Bundle('favicon.js')
assets.register('favicon', favicon)

js = Bundle('scripts.js')
assets.register('scripts', js)
