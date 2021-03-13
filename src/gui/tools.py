def blit_alpha(target, source, location, opacity):
    source.set_alpha(opacity)
    target.blit(source, location)
