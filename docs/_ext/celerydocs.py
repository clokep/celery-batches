# This is partially copied from celery/docs/_ext/celerydocs.py.

def setup(app):
    app.add_crossref_type(
        directivename='sig',
        rolename='sig',
        indextemplate='pair: %s; sig',
    )

    return {
        'parallel_read_safe': True
    }
