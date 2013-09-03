# -*- coding: utf-8 -*-
#@PydevCodeAnalysisIgnore
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'LuminaUser'
        db.create_table(u'lumina_luminauser', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('password', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('last_login', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('is_superuser', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('username', self.gf('django.db.models.fields.CharField')(unique=True, max_length=30)),
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
            ('last_name', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75, blank=True)),
            ('is_staff', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('date_joined', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('user_type', self.gf('django.db.models.fields.CharField')(default='P', max_length=1)),
            ('studio', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='photographers', null=True, to=orm['lumina.Studio'])),
            ('user_for_customer', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='users', null=True, to=orm['lumina.Customer'])),
        ))
        db.send_create_signal(u'lumina', ['LuminaUser'])

        # Adding M2M table for field groups on 'LuminaUser'
        m2m_table_name = db.shorten_name(u'lumina_luminauser_groups')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('luminauser', models.ForeignKey(orm[u'lumina.luminauser'], null=False)),
            ('group', models.ForeignKey(orm[u'auth.group'], null=False))
        ))
        db.create_unique(m2m_table_name, ['luminauser_id', 'group_id'])

        # Adding M2M table for field user_permissions on 'LuminaUser'
        m2m_table_name = db.shorten_name(u'lumina_luminauser_user_permissions')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('luminauser', models.ForeignKey(orm[u'lumina.luminauser'], null=False)),
            ('permission', models.ForeignKey(orm[u'auth.permission'], null=False))
        ))
        db.create_unique(m2m_table_name, ['luminauser_id', 'permission_id'])

        # Adding model 'Studio'
        db.create_table(u'lumina_studio', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal(u'lumina', ['Studio'])

        # Adding model 'Customer'
        db.create_table(u'lumina_customer', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('studio', self.gf('django.db.models.fields.related.ForeignKey')(related_name='customers', to=orm['lumina.Studio'])),
            ('address', self.gf('django.db.models.fields.TextField')()),
            ('phone', self.gf('django.db.models.fields.CharField')(max_length=20)),
        ))
        db.send_create_signal(u'lumina', ['Customer'])

        # Adding model 'Session'
        db.create_table(u'lumina_session', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=300)),
            ('studio', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['lumina.Studio'])),
            ('photographer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['lumina.LuminaUser'])),
            ('customer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['lumina.Customer'], null=True, blank=True)),
        ))
        db.send_create_signal(u'lumina', ['Session'])

        # Adding M2M table for field shared_with on 'Session'
        m2m_table_name = db.shorten_name(u'lumina_session_shared_with')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('session', models.ForeignKey(orm[u'lumina.session'], null=False)),
            ('customer', models.ForeignKey(orm[u'lumina.customer'], null=False))
        ))
        db.create_unique(m2m_table_name, ['session_id', 'customer_id'])

        # Adding model 'SharedSessionByEmail'
        db.create_table(u'lumina_sharedsessionbyemail', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('shared_with', self.gf('django.db.models.fields.EmailField')(max_length=254)),
            ('studio', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['lumina.Studio'])),
            ('session', self.gf('django.db.models.fields.related.ForeignKey')(related_name='shares_via_email', to=orm['lumina.Session'])),
            ('random_hash', self.gf('django.db.models.fields.CharField')(unique=True, max_length=36)),
        ))
        db.send_create_signal(u'lumina', ['SharedSessionByEmail'])

        # Adding model 'ImageSelection'
        db.create_table(u'lumina_imageselection', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('studio', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', to=orm['lumina.Studio'])),
            ('session', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['lumina.Session'])),
            ('customer', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', to=orm['lumina.Customer'])),
            ('image_quantity', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('status', self.gf('django.db.models.fields.CharField')(default='W', max_length=1)),
        ))
        db.send_create_signal(u'lumina', ['ImageSelection'])

        # Adding M2M table for field selected_images on 'ImageSelection'
        m2m_table_name = db.shorten_name(u'lumina_imageselection_selected_images')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('imageselection', models.ForeignKey(orm[u'lumina.imageselection'], null=False)),
            ('image', models.ForeignKey(orm[u'lumina.image'], null=False))
        ))
        db.create_unique(m2m_table_name, ['imageselection_id', 'image_id'])

        # Adding model 'Image'
        db.create_table(u'lumina_image', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('image', self.gf('django.db.models.fields.files.FileField')(max_length=300)),
            ('size', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('original_filename', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('content_type', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('studio', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['lumina.Studio'])),
            ('session', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['lumina.Session'], null=True)),
        ))
        db.send_create_signal(u'lumina', ['Image'])


    def backwards(self, orm):
        # Deleting model 'LuminaUser'
        db.delete_table(u'lumina_luminauser')

        # Removing M2M table for field groups on 'LuminaUser'
        db.delete_table(db.shorten_name(u'lumina_luminauser_groups'))

        # Removing M2M table for field user_permissions on 'LuminaUser'
        db.delete_table(db.shorten_name(u'lumina_luminauser_user_permissions'))

        # Deleting model 'Studio'
        db.delete_table(u'lumina_studio')

        # Deleting model 'Customer'
        db.delete_table(u'lumina_customer')

        # Deleting model 'Session'
        db.delete_table(u'lumina_session')

        # Removing M2M table for field shared_with on 'Session'
        db.delete_table(db.shorten_name(u'lumina_session_shared_with'))

        # Deleting model 'SharedSessionByEmail'
        db.delete_table(u'lumina_sharedsessionbyemail')

        # Deleting model 'ImageSelection'
        db.delete_table(u'lumina_imageselection')

        # Removing M2M table for field selected_images on 'ImageSelection'
        db.delete_table(db.shorten_name(u'lumina_imageselection_selected_images'))

        # Deleting model 'Image'
        db.delete_table(u'lumina_image')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'lumina.customer': {
            'Meta': {'object_name': 'Customer'},
            'address': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'studio': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'customers'", 'to': u"orm['lumina.Studio']"})
        },
        u'lumina.image': {
            'Meta': {'object_name': 'Image'},
            'content_type': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.FileField', [], {'max_length': '300'}),
            'original_filename': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'session': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['lumina.Session']", 'null': 'True'}),
            'size': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'studio': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['lumina.Studio']"})
        },
        u'lumina.imageselection': {
            'Meta': {'object_name': 'ImageSelection'},
            'customer': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': u"orm['lumina.Customer']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image_quantity': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'selected_images': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['lumina.Image']", 'symmetrical': 'False', 'blank': 'True'}),
            'session': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['lumina.Session']"}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'W'", 'max_length': '1'}),
            'studio': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': u"orm['lumina.Studio']"})
        },
        u'lumina.luminauser': {
            'Meta': {'object_name': 'LuminaUser'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'studio': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'photographers'", 'null': 'True', 'to': u"orm['lumina.Studio']"}),
            'user_for_customer': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'users'", 'null': 'True', 'to': u"orm['lumina.Customer']"}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'user_type': ('django.db.models.fields.CharField', [], {'default': "'P'", 'max_length': '1'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'lumina.session': {
            'Meta': {'object_name': 'Session'},
            'customer': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['lumina.Customer']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'photographer': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['lumina.LuminaUser']"}),
            'shared_with': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'sessions_shared_with_me'", 'blank': 'True', 'to': u"orm['lumina.Customer']"}),
            'studio': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['lumina.Studio']"})
        },
        u'lumina.sharedsessionbyemail': {
            'Meta': {'object_name': 'SharedSessionByEmail'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'random_hash': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '36'}),
            'session': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'shares_via_email'", 'to': u"orm['lumina.Session']"}),
            'shared_with': ('django.db.models.fields.EmailField', [], {'max_length': '254'}),
            'studio': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['lumina.Studio']"})
        },
        u'lumina.studio': {
            'Meta': {'object_name': 'Studio'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['lumina']