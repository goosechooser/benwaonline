from flask_assets import Environment, Bundle
assets = Environment()

css = Bundle('style.css', filters='cssmin', output='min_style.%(version)s.css')
assets.register('css_min', css)
