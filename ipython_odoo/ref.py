
def generate_ref(env):
    env.cr.execute("""
        select
            module,
            string_agg(name, ',')
        from
            ir_model_data
        where
            module != '__export__'
            and name not like '%-%'
            and name not like '% %'
            and name not like '%@%'
            and name !~ '^\d'
        group by
            module
        """)

    Ref_attrs = {}
    for module, names in env.cr.fetchall():
        ModuleRefs = type('ModuleRefs', (), {
            # '__slots__': names.split(',') + ['_module', '_env'],
            '__slots__': names.split(','),
            '_env': env,
            '_module': module,
            '__getattr__': lambda self, name: self._env.ref(self._module + '.' + name),
        })
        Ref_attrs[module] = ModuleRefs()

    Ref_attrs['__slots__'] = list(Ref_attrs.keys())
    Ref = type('Ref', (), Ref_attrs)

    return Ref()
