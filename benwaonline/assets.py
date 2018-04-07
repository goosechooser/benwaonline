from flask_assets import Environment, Bundle
assets = Environment()

css = Bundle('style.css', output='style_busted.%(version)s.css')
assets.register('css_min', css)

jquery = Bundle('jquery.js')
assets.register('jquery', jquery)

favicon = Bundle('favicon.js')
assets.register('favicon', favicon)

js = Bundle('scripts.js')
assets.register('nice', js)
