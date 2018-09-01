from imagekit import ImageSpec, register
from imagekit.processors import ResizeToFit


# TODO: Can I remove this?
class HeadShot(ImageSpec):
    processors = [ResizeToFit(100, 100)]
    format = 'JPEG'
    options = {'quality': 60}

register.generator('tas:Headshot', HeadShot)
