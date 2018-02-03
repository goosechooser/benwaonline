from flask_assets import Environment, Bundle
assets = Environment()

css = Bundle('style.css', output='style_busted.%(version)s.css')
assets.register('css_min', css)

js = Bundle('scripts.js', output='nice.js')
assets.register('nice', js)
