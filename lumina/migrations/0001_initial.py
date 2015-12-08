# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import lumina.models
import django.core.validators
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
    ]

    operations = [
        migrations.CreateModel(
            name='LuminaUser',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(verbose_name='last login', blank=True, null=True)),
                ('is_superuser', models.BooleanField(help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status', default=False)),
                ('username', models.CharField(help_text='Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only.', error_messages={'unique': 'A user with that username already exists.'}, max_length=30, unique=True, verbose_name='username', validators=[django.core.validators.RegexValidator('^[\\w.@+-]+$', 'Enter a valid username. This value may contain only letters, numbers and @/./+/-/_ characters.', 'invalid')])),
                ('first_name', models.CharField(max_length=30, blank=True, verbose_name='first name')),
                ('last_name', models.CharField(max_length=30, blank=True, verbose_name='last name')),
                ('email', models.EmailField(max_length=254, blank=True, verbose_name='email address')),
                ('is_staff', models.BooleanField(help_text='Designates whether the user can log into this admin site.', verbose_name='staff status', default=False)),
                ('is_active', models.BooleanField(help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active', default=True)),
                ('date_joined', models.DateTimeField(verbose_name='date joined', default=django.utils.timezone.now)),
                ('user_type', models.CharField(max_length=1, choices=[('P', 'Fotografo'), ('C', 'Cliente')], default='P')),
                ('phone', models.CharField(max_length=20, verbose_name='Teléfono', blank=True, null=True)),
                ('cellphone', models.CharField(max_length=20, verbose_name='Celular', blank=True, null=True)),
                ('alternative_email', models.EmailField(max_length=254, verbose_name='Email alternativo', blank=True, null=True)),
                ('notes', models.TextField(verbose_name='Notas', blank=True, null=True)),
                ('groups', models.ManyToManyField(help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', to='auth.Group', related_query_name='user', blank=True, verbose_name='groups', related_name='user_set')),
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
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='nombre')),
                ('address', models.TextField(blank=True, verbose_name='dirección')),
                ('phone', models.CharField(max_length=20, blank=True, verbose_name='teléfono')),
                ('city', models.CharField(max_length=40, verbose_name='ciudad', blank=True, null=True)),
                ('cuit', models.CharField(max_length=13, blank=True, null=True)),
                ('iva', models.CharField(max_length=1, default=None, blank=True, choices=[('R', 'Responsable Inscripto'), ('M', 'Responsable Monotributo'), ('E', 'Responsable Excento'), ('F', 'Consumidor Final')], null=True)),
                ('ingresos_brutos', models.CharField(max_length=20, blank=True, null=True)),
                ('notes', models.TextField(verbose_name='Notas', blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='CustomerType',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='nombre')),
                ('archived', models.BooleanField(verbose_name='Archivado', default=False)),
            ],
            options={
                'verbose_name_plural': 'tipos de cliente',
                'verbose_name': 'tipo de cliente',
            },
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('image', models.FileField(upload_to='images/%Y/%m/%d', max_length=300, verbose_name='imagen', blank=True, null=True)),
                ('size', models.PositiveIntegerField(verbose_name='tamaño', blank=True, null=True)),
                ('original_filename', models.CharField(max_length=128, verbose_name='nombre de archivo original', blank=True, null=True)),
                ('content_type', models.CharField(max_length=64, verbose_name='tipo de contenido', blank=True, null=True)),
                ('thumbnail_image', models.FileField(upload_to='images/%Y/%m/%d', max_length=300, verbose_name='previsualizacion', blank=True, null=True)),
                ('thumbnail_size', models.PositiveIntegerField(verbose_name='tamaño de la previsualizacion', blank=True, null=True)),
                ('thumbnail_original_filename', models.CharField(max_length=128, verbose_name='nombre de archivo (en cliente) de previsualizacion', blank=True, null=True)),
                ('thumbnail_content_type', models.CharField(max_length=64, verbose_name='tipo de contenido de previsualizacion', blank=True, null=True)),
                ('original_file_checksum', models.CharField(max_length=64, verbose_name='checksum de archivo original', blank=True, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='ImageSelection',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('image_quantity', models.PositiveIntegerField(verbose_name='cantidad de imágenes')),
                ('status', models.CharField(max_length=1, verbose_name='estado', choices=[('W', 'Esperando selección de cliente'), ('S', 'Seleccion realizada')], default='W')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('customer', models.ForeignKey(to='lumina.Customer', verbose_name='cliente', related_name='+')),
            ],
        ),
        migrations.CreateModel(
            name='PreviewSize',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('max_size', models.PositiveIntegerField(verbose_name='Tamaño máximo')),
                ('archived', models.BooleanField(verbose_name='Archivado', default=False)),
            ],
            options={
                'ordering': ['max_size'],
                'verbose_name_plural': 'tamaños de previsualización',
                'verbose_name': 'tamaño de previsualización',
            },
        ),
        migrations.CreateModel(
            name='Session',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('name', models.CharField(max_length=300, verbose_name='Nombre')),
                ('worked_hours', models.PositiveIntegerField(verbose_name='horas trabajadas', default=0)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('archived', models.BooleanField(verbose_name='Archivada', default=False)),
                ('album_icon', models.ForeignKey(to='lumina.Image', blank=True, null=True, related_name='+')),
                ('customer', models.ForeignKey(to='lumina.Customer', verbose_name='cliente')),
                ('photographer', models.ForeignKey(to=settings.AUTH_USER_MODEL, verbose_name='fotógrafo')),
            ],
        ),
        migrations.CreateModel(
            name='SessionQuote',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('name', models.CharField(max_length=300, verbose_name='nombre')),
                ('image_quantity', models.PositiveIntegerField(verbose_name='cantidad de imágenes')),
                ('status', models.CharField(max_length=1, verbose_name='estado', choices=[('Q', 'Siendo creado por fotografo'), ('S', 'Esperando aceptacion de cliente'), ('A', 'Aceptado por el cliente'), ('R', 'Rechazado por el cliente'), ('E', 'Cancelado por fotografo')], default='Q')),
                ('cost', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='costo')),
                ('terms', models.TextField(verbose_name='términos')),
                ('accepted_rejected_at', models.DateTimeField(blank=True, null=True)),
                ('stipulated_date', models.DateField(verbose_name='fecha de entrega pactada')),
                ('stipulated_down_payment', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='entrega inicial pactada')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('archived', models.BooleanField(verbose_name='Archivado', default=False)),
            ],
        ),
        migrations.CreateModel(
            name='SessionQuoteAlternative',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
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
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='nombre')),
                ('archived', models.BooleanField(verbose_name='Archivado', default=False)),
            ],
            options={
                'verbose_name_plural': 'tipos de sesión',
                'verbose_name': 'tipo de sesión',
            },
        ),
        migrations.CreateModel(
            name='SharedSessionByEmail',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('shared_with', models.EmailField(max_length=254, verbose_name='compartida con')),
                ('random_hash', models.CharField(max_length=36, unique=True)),
                ('session', models.ForeignKey(to='lumina.Session', verbose_name='sesión', related_name='shares_via_email')),
            ],
        ),
        migrations.CreateModel(
            name='Studio',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Nombre del estudio')),
                ('default_terms', models.TextField(verbose_name='Términos y condiciones por default')),
                ('watermark_text', models.CharField(max_length=40, verbose_name='Marca de agua', default='')),
            ],
        ),
        migrations.CreateModel(
            name='UserPreferences',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('send_emails', models.BooleanField(verbose_name='Enviar emails', default=True)),
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
            field=models.ForeignKey(to='lumina.SessionQuoteAlternative', blank=True, verbose_name='presupuesto alternativo', related_name='+', null=True, on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.AddField(
            model_name='sessionquote',
            name='accepted_rejected_by',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, blank=True, null=True, related_name='+'),
        ),
        migrations.AddField(
            model_name='sessionquote',
            name='customer',
            field=models.ForeignKey(to='lumina.Customer', verbose_name='cliente', related_name='session_quotes'),
        ),
        migrations.AddField(
            model_name='sessionquote',
            name='session',
            field=models.ForeignKey(to='lumina.Session', blank=True, verbose_name='Sesión', related_name='quotes', null=True, on_delete=django.db.models.deletion.SET_NULL),
        ),
        migrations.AddField(
            model_name='sessionquote',
            name='studio',
            field=models.ForeignKey(to='lumina.Studio', verbose_name='estudio', related_name='session_quotes'),
        ),
        migrations.AddField(
            model_name='session',
            name='session_type',
            field=models.ForeignKey(to='lumina.SessionType', verbose_name='tipo de sesión', related_name='+'),
        ),
        migrations.AddField(
            model_name='session',
            name='shared_with',
            field=models.ManyToManyField(related_name='sessions_shared_with_me', to='lumina.Customer', blank=True, verbose_name='Compartida con'),
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
            field=models.ForeignKey(to='lumina.PreviewSize', verbose_name='tamaño de previsualización', null=True),
        ),
        migrations.AddField(
            model_name='imageselection',
            name='quote',
            field=models.ForeignKey(to='lumina.SessionQuote', blank=True, verbose_name='presupuesto', null=True),
        ),
        migrations.AddField(
            model_name='imageselection',
            name='selected_images',
            field=models.ManyToManyField(to='lumina.Image', blank=True, verbose_name='imágenes seleccionadas'),
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
            field=models.ForeignKey(to='lumina.CustomerType', verbose_name='tipo de cliente', related_name='+', null=True),
        ),
        migrations.AddField(
            model_name='customer',
            name='studio',
            field=models.ForeignKey(to='lumina.Studio', verbose_name='estudio', related_name='customers'),
        ),
        migrations.AddField(
            model_name='luminauser',
            name='studio',
            field=models.ForeignKey(to='lumina.Studio', blank=True, verbose_name='Estudio', related_name='photographers', null=True),
        ),
        migrations.AddField(
            model_name='luminauser',
            name='user_for_customer',
            field=models.ForeignKey(to='lumina.Customer', blank=True, verbose_name='Cliente', related_name='users', null=True),
        ),
        migrations.AddField(
            model_name='luminauser',
            name='user_permissions',
            field=models.ManyToManyField(help_text='Specific permissions for this user.', to='auth.Permission', related_query_name='user', blank=True, verbose_name='user permissions', related_name='user_set'),
        ),
        migrations.AlterUniqueTogether(
            name='sessiontype',
            unique_together=set([('studio', 'name')]),
        ),
        migrations.AlterUniqueTogether(
            name='sessionquotealternative',
            unique_together=set([('session_quote', 'image_quantity')]),
        ),
        migrations.AlterUniqueTogether(
            name='previewsize',
            unique_together=set([('max_size', 'studio')]),
        ),
        migrations.AlterUniqueTogether(
            name='customertype',
            unique_together=set([('studio', 'name')]),
        ),
    ]
