from django.db import migrations


def seed_motto(apps, schema_editor):
    # Blank on purpose — this is a fork of EAEvents; the motto is
    # Living Manna's own to set later (via admin or a future data migration),
    # not Elijah's Ark Mission's "ARISE. BUILD. COMPEL".
    SiteSettings = apps.get_model('events', 'SiteSettings')
    SiteSettings.objects.get_or_create(pk=1, defaults={'motto': ''})


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0011_sitesettings'),
    ]

    operations = [
        migrations.RunPython(seed_motto, noop),
    ]
