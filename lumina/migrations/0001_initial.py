# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators
import lumina.models
from django.conf import settings
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
    ]

    operations = [
        migrations.CreateModel(
            name='LuminaUser',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(null=True, blank=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(help_text='Designates that this user has all permissions without explicitly assigning them.', default=False, verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, max_length=30, validators=[django.core.validators.RegexValidator('^[\\w.@+-]+$', 'Enter a valid username. This value may contain only letters, numbers and @/./+/-/_ characters.', 'invalid')], help_text='Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only.', unique=True, verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=30, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=30, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(help_text='Designates whether the user can log into this admin site.', default=False, verbose_name='staff status')),
                ('is_active', models.BooleanField(help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', default=True, verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('user_type', models.CharField(choices=[('P', 'Fotografo'), ('C', 'Cliente')], default='P', max_length=1)),
                ('phone', models.CharField(blank=True, null=True, max_length=20, verbose_name='Teléfono')),
                ('cellphone', models.CharField(blank=True, null=True, max_length=20, verbose_name='Celular')),
                ('alternative_email', models.EmailField(blank=True, null=True, max_length=254, verbose_name='Email alternativo')),
                ('notes', models.TextField(null=True, blank=True, verbose_name='Notas')),
                ('groups', models.ManyToManyField(blank=True, to='auth.Group', help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_query_name='user', verbose_name='groups', related_name='user_set')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', lumina.models.LuminaUserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('name', models.CharField(max_length=100, verbose_name='nombre')),
                ('address', models.TextField(blank=True, verbose_name='dirección')),
                ('phone', models.CharField(blank=True, max_length=20, verbose_name='teléfono')),
                ('city', models.CharField(blank=True, null=True, max_length=40, verbose_name='ciudad')),
                ('cuit', models.CharField(blank=True, null=True, max_length=13)),
                ('iva', models.CharField(choices=[('R', 'Responsable Inscripto'), ('M', 'Responsable Monotributo'), ('E', 'Responsable Excento'), ('F', 'Consumidor Final')], blank=True, default=None, null=True, max_length=1)),
                ('ingresos_brutos', models.CharField(blank=True, null=True, max_length=20)),
                ('notes', models.TextField(null=True, blank=True, verbose_name='Notas')),
            ],
        ),
        migrations.CreateModel(
            name='CustomerType',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('name', models.CharField(max_length=100, verbose_name='tipo de cliente')),
            ],
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('image', models.FileField(upload_to='images/%Y/%m/%d', blank=True, null=True, max_length=300, verbose_name='imagen')),
                ('size', models.PositiveIntegerField(null=True, blank=True, verbose_name='tamaño')),
                ('original_filename', models.CharField(blank=True, null=True, max_length=128, verbose_name='nombre de archivo original')),
                ('content_type', models.CharField(blank=True, null=True, max_length=64, verbose_name='tipo de contenido')),
                ('thumbnail_image', models.FileField(upload_to='images/%Y/%m/%d', blank=True, null=True, max_length=300, verbose_name='previsualizacion')),
                ('thumbnail_size', models.PositiveIntegerField(null=True, blank=True, verbose_name='tamaño de la previsualizacion')),
                ('thumbnail_original_filename', models.CharField(blank=True, null=True, max_length=128, verbose_name='nombre de archivo (en cliente) de previsualizacion')),
                ('thumbnail_content_type', models.CharField(blank=True, null=True, max_length=64, verbose_name='tipo de contenido de previsualizacion')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='ImageSelection',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('image_quantity', models.PositiveIntegerField(verbose_name='cantidad de imágenes')),
                ('status', models.CharField(choices=[('W', 'Esperando selección de cliente'), ('S', 'Seleccion realizada')], default='W', max_length=1, verbose_name='estado')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('customer', models.ForeignKey(to='lumina.Customer', verbose_name='cliente', related_name='+')),
            ],
        ),
        migrations.CreateModel(
            name='PreviewSize',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('max_size', models.PositiveIntegerField(null=True, blank=True, verbose_name='Tamaño máximo')),
            ],
            options={
                'ordering': ['max_size'],
            },
        ),
        migrations.CreateModel(
            name='Session',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('name', models.CharField(max_length=300, verbose_name='Nombre')),
                ('worked_hours', models.PositiveIntegerField(default=0, verbose_name='horas trabajadas')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('archived', models.BooleanField(default=False, verbose_name='Archivada')),
                ('customer', models.ForeignKey(blank=True, to='lumina.Customer', null=True, verbose_name='cliente')),
                ('photographer', models.ForeignKey(to=settings.AUTH_USER_MODEL, verbose_name='fotógrafo')),
            ],
        ),
        migrations.CreateModel(
            name='SessionQuote',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('name', models.CharField(max_length=300, verbose_name='nombre')),
                ('image_quantity', models.PositiveIntegerField(verbose_name='cantidad de imágenes')),
                ('status', models.CharField(choices=[('Q', 'Siendo creado por fotografo'), ('S', 'Esperando aceptacion de cliente'), ('A', 'Aceptado por el cliente'), ('R', 'Rechazado por el cliente'), ('E', 'Cancelado por fotografo')], default='Q', max_length=1, verbose_name='estado')),
                ('cost', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='costo')),
                ('terms', models.TextField(verbose_name='términos')),
                ('accepted_rejected_at', models.DateTimeField(null=True, blank=True)),
                ('stipulated_date', models.DateTimeField(verbose_name='fecha de entrega pactada')),
                ('stipulated_down_payment', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='entrega inicial pactada')),
                ('give_full_quality_images', models.BooleanField(default=True, verbose_name='Entrega JPGs de máxima calidad')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('archived', models.BooleanField(default=False, verbose_name='Archivado')),
            ],
        ),
        migrations.CreateModel(
            name='SessionQuoteAlternative',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('image_quantity', models.PositiveIntegerField(verbose_name='cantidad de imágenes')),
                ('cost', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='costo')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('session_quote', models.ForeignKey(to='lumina.SessionQuote', verbose_name='presupuesto', related_name='quote_alternatives')),
            ],
            options={
                'ordering': ['image_quantity'],
            },
        ),
        migrations.CreateModel(
            name='SessionType',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('name', models.CharField(max_length=100, verbose_name='tipo de sesión')),
            ],
        ),
        migrations.CreateModel(
            name='SharedSessionByEmail',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('shared_with', models.EmailField(max_length=254, verbose_name='compartida con')),
                ('random_hash', models.CharField(unique=True, max_length=36)),
                ('session', models.ForeignKey(to='lumina.Session', verbose_name='sesión', related_name='shares_via_email')),
            ],
        ),
        migrations.CreateModel(
            name='Studio',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('name', models.CharField(max_length=100, verbose_name='Nombre')),
                ('default_terms', models.TextField(null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='UserPreferences',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('send_emails', models.BooleanField(default=True, verbose_name='Enviar emails')),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL, related_name='preferences')),
            ],
        ),
        migrations.AddField(
            model_name='sharedsessionbyemail',
            name='studio',
            field=models.ForeignKey(to='lumina.Studio', verbose_name='estudio'),
        ),
        migrations.AddField(
            model_name='sessiontype',
            name='studio',
            field=models.ForeignKey(to='lumina.Studio', verbose_name='estudio', related_name='session_types'),
        ),
        migrations.AddField(
            model_name='sessionquote',
            name='accepted_quote_alternative',
            field=models.ForeignKey(blank=True, to='lumina.SessionQuoteAlternative', related_name='+', on_delete=django.db.models.deletion.PROTECT, null=True, verbose_name='presupuesto alternativo'),
        ),
        migrations.AddField(
            model_name='sessionquote',
            name='accepted_rejected_by',
            field=models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, related_name='+', null=True),
        ),
        migrations.AddField(
            model_name='sessionquote',
            name='customer',
            field=models.ForeignKey(to='lumina.Customer', verbose_name='cliente', related_name='session_quotes'),
        ),
        migrations.AddField(
            model_name='sessionquote',
            name='session',
            field=models.ForeignKey(blank=True, to='lumina.Session', related_name='quotes', null=True, verbose_name='Sesión'),
        ),
        migrations.AddField(
            model_name='sessionquote',
            name='studio',
            field=models.ForeignKey(to='lumina.Studio', verbose_name='estudio', related_name='session_quotes'),
        ),
        migrations.AddField(
            model_name='session',
            name='session_type',
            field=models.ForeignKey(to='lumina.SessionType', related_name='+', verbose_name='tipo de sesión', null=True),
        ),
        migrations.AddField(
            model_name='session',
            name='shared_with',
            field=models.ManyToManyField(related_name='sessions_shared_with_me', blank=True, to='lumina.Customer', verbose_name='Compartida con'),
        ),
        migrations.AddField(
            model_name='session',
            name='studio',
            field=models.ForeignKey(to='lumina.Studio', verbose_name='estudio'),
        ),
        migrations.AddField(
            model_name='previewsize',
            name='studio',
            field=models.ForeignKey(to='lumina.Studio', verbose_name='estudio', related_name='preview_sizes'),
        ),
        migrations.AddField(
            model_name='imageselection',
            name='preview_size',
            field=models.ForeignKey(blank=True, to='lumina.PreviewSize', null=True, verbose_name='tamaño de previsualización'),
        ),
        migrations.AddField(
            model_name='imageselection',
            name='quote',
            field=models.ForeignKey(blank=True, to='lumina.SessionQuote', null=True, verbose_name='presupuesto'),
        ),
        migrations.AddField(
            model_name='imageselection',
            name='selected_images',
            field=models.ManyToManyField(blank=True, to='lumina.Image', verbose_name='imágenes seleccionadas'),
        ),
        migrations.AddField(
            model_name='imageselection',
            name='session',
            field=models.ForeignKey(to='lumina.Session', verbose_name='sesión'),
        ),
        migrations.AddField(
            model_name='imageselection',
            name='studio',
            field=models.ForeignKey(to='lumina.Studio', verbose_name='estudio', related_name='+'),
        ),
        migrations.AddField(
            model_name='image',
            name='session',
            field=models.ForeignKey(to='lumina.Session', verbose_name='sesión', null=True),
        ),
        migrations.AddField(
            model_name='image',
            name='studio',
            field=models.ForeignKey(to='lumina.Studio', verbose_name='estudio'),
        ),
        migrations.AddField(
            model_name='customertype',
            name='studio',
            field=models.ForeignKey(to='lumina.Studio', verbose_name='estudio', related_name='customer_types'),
        ),
        migrations.AddField(
            model_name='customer',
            name='customer_type',
            field=models.ForeignKey(to='lumina.CustomerType', related_name='+', verbose_name='tipo de cliente', null=True),
        ),
        migrations.AddField(
            model_name='customer',
            name='studio',
            field=models.ForeignKey(to='lumina.Studio', verbose_name='estudio', related_name='customers'),
        ),
        migrations.AddField(
            model_name='luminauser',
            name='studio',
            field=models.ForeignKey(blank=True, to='lumina.Studio', related_name='photographers', null=True, verbose_name='Estudio'),
        ),
        migrations.AddField(
            model_name='luminauser',
            name='user_for_customer',
            field=models.ForeignKey(blank=True, to='lumina.Customer', related_name='users', null=True, verbose_name='Cliente'),
        ),
        migrations.AddField(
            model_name='luminauser',
            name='user_permissions',
            field=models.ManyToManyField(blank=True, to='auth.Permission', help_text='Specific permissions for this user.', related_query_name='user', verbose_name='user permissions', related_name='user_set'),
        ),
        migrations.AlterUniqueTogether(
            name='sessionquotealternative',
            unique_together=set([('session_quote', 'image_quantity')]),
        ),
        migrations.AlterUniqueTogether(
            name='previewsize',
            unique_together=set([('max_size', 'studio')]),
        ),
    ]
