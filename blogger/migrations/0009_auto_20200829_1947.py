# Generated by Django 3.0 on 2020-08-29 19:47

from django.db import migrations, models
import django.db.models.deletion
import modelcluster.fields
import wagtail.core.blocks
import wagtail.core.fields


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailimages', '0022_uploadedimage'),
        ('blogger', '0008_blogpage_categories'),
    ]

    operations = [
        migrations.CreateModel(
            name='BlogAuthor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=250)),
                ('website', models.URLField(blank=True, null=True)),
                ('image', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='wagtailimages.Image')),
            ],
            options={
                'verbose_name': 'Post Authors',
            },
        ),
        migrations.AddField(
            model_name='blogpage',
            name='release',
            field=models.IntegerField(default=2000),
        ),
        migrations.AddField(
            model_name='blogpage',
            name='sequel',
            field=wagtail.core.fields.StreamField([('title_and_text', wagtail.core.blocks.StructBlock([('title', wagtail.core.blocks.CharBlock(help_text='Add your title', required=True)), ('text', wagtail.core.blocks.TextBlock(help_text='Add your text', required=True))]))], blank=True, null=True),
        ),
        migrations.CreateModel(
            name='BlogPageAuthor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sort_order', models.IntegerField(blank=True, editable=False, null=True)),
                ('author', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='blogger.BlogAuthor')),
                ('page', modelcluster.fields.ParentalKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='post_author', to='blogger.BlogPage')),
            ],
            options={
                'ordering': ['sort_order'],
                'abstract': False,
            },
        ),
    ]
