# coding=utf8
__import__('os').environ['TZ'] = 'UTC'
__import__('pkg_resources').declare_namespace('odoo.addons')

from .magic import MyMagics

# http://localhost:63342/api/file//home/voronin/projects/sintez_addons/sintez_base/__manifest__.py:1



def load_ipython_extension(ipython):
    # The `ipython` argument is the currently active `InteractiveShell`
    # instance, which can be used in any way. This allows you to register
    # new magics or aliases, for example.
    ipython.register_magics(MyMagics)


def unload_ipython_extension(ipython):
    # If you want your extension to be unloadable, put that logic here.
    pass
