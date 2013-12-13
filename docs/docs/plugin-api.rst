The Plugin API
==============

**There's no plugin API yet. We're focusing our efforts on improving the core.**

The plugin api will look something like this::
    
    plugins:
        - depl_my_django:
            path: depl_plugins/my_django
        - depl_sinatra  # just a plugin in python path
            
    deploy:
        - my_django
        - my_sinatra

Obviously we would still need to define the exact way of how to write that
plugin. But as you can see it's probably going to be pretty easy to write a
plugin (just create a new python package).
