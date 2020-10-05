# taken from https://code.djangoproject.com/wiki/DynamicModels and http://www.agmweb.ca/blog/andy/2249/
from django import forms
from django.db import models, connection
from django.apps import apps as cache
from django.core.management import color
from django.contrib import admin

"""
This module is cancer. This is a contradition on itself.
The motivation to this kind of code is the reason _NOT_ to do it.
From the links above:

"The advantages of not having to declare a model in Python source should become clear shortly."

... except that they never do, only the problems of doing this do. Though they were already
crystal clear to any season programmer.

Waste of anyone's time. Kill with fire!

"""


def create(name, fields=None, app_label='', module='', options=None, admin_opts=None):
    """
    Create specified model
    """

    class Meta:
        # Using type('Meta', ...) gives a dictproxy error during model creation
        managed = False
        pass

    if app_label:
        # app_label must be set using the Meta inner class
        setattr(Meta, 'app_label', app_label)

    # Update Meta with any options that were provided
    if options is not None:
        for key, value in options.items():
            setattr(Meta, key, value)

    # Set up a dictionary to simulate declarations within a class
    attrs = {'__module__': module, 'Meta': Meta}

    # Add in any fields that were provided
    if fields:
        attrs.update(fields)

    # Create the class, which automatically triggers ModelBase processing
    model = type(name, (models.Model,), attrs)

    # Ensure that the dynamic class is not cached
    cache.all_models[app_label].pop(model._meta.object_name, None)

    # Create an Admin class if admin options were provided
    if admin_opts is not None:
        class Admin(admin.ModelAdmin):
            pass

        for key, value in admin_opts:
            setattr(Admin, key, value)
        admin.site.register(model, Admin)

    return model


def install(model):
    # Standard syncdb expects models to be in reliable locations,
    # so dynamic models need to bypass django.core.management.syncdb.
    # On the plus side, this allows individual models to be installed
    # without installing the entire project structure.
    # On the other hand, this means that things like relationships and
    # indexes will have to be handled manually.
    # This installs only the basic table definition.

    with connection.schema_editor() as schema_editor:
        schema_editor.create_model(model)


def to_form(model, fields=None):
    class Meta:
        pass

    Meta.model = model
    Meta.fields = '__all__'

    attrs = {'Meta': Meta}
    if fields:
        attrs.update(fields)
    form = type('modelform', (forms.ModelForm,), attrs)
    return form
