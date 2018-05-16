from flask_assets import Environment, Bundle
assets = Environment()

css = Bundle('css/style.css', output='style_busted.%(version)s.css')
assets.register('css_min', css)

favicon = Bundle('favicon.js')
assets.register('favicon', favicon)

js = Bundle('scripts.js', output='scripts_busted.%(version)s.js')
assets.register('scripts', js)
