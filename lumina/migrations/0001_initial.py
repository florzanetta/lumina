#@PydevCodeAnalysisIgnore
# -*- coding: utf-8 -*-
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
            ('customer_of', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='customers', null=True, to=orm['lumina.LuminaUser'])),
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

        # Adding model 'Album'
        db.create_table(u'lumina_album', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=300)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['lumina.LuminaUser'])),
        ))
        db.send_create_signal(u'lumina', ['Album'])

        # Adding M2M table for field shared_with on 'Album'
        m2m_table_name = db.shorten_name(u'lumina_album_shared_with')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('album', models.ForeignKey(orm[u'lumina.album'], null=False)),
            ('luminauser', models.ForeignKey(orm[u'lumina.luminauser'], null=False))
        ))
        db.create_unique(m2m_table_name, ['album_id', 'luminauser_id'])

        # Adding model 'SharedAlbum'
        db.create_table(u'lumina_sharedalbum', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('shared_with', self.gf('django.db.models.fields.EmailField')(max_length=254)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['lumina.LuminaUser'])),
            ('album', self.gf('django.db.models.fields.related.ForeignKey')(related_name='shares_via_email', to=orm['lumina.Album'])),
            ('random_hash', self.gf('django.db.models.fields.CharField')(unique=True, max_length=36)),
        ))
        db.send_create_signal(u'lumina', ['SharedAlbum'])

        # Adding model 'ImageSelection'
        db.create_table(u'lumina_imageselection', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', to=orm['lumina.LuminaUser'])),
            ('album', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['lumina.Album'])),
            ('customer', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', to=orm['lumina.LuminaUser'])),
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
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['lumina.LuminaUser'])),
            ('album', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['lumina.Album'], null=True)),
        ))
        db.send_create_signal(u'lumina', ['Image'])


    def backwards(self, orm):
        # Deleting model 'LuminaUser'
        db.delete_table(u'lumina_luminauser')

        # Removing M2M table for field groups on 'LuminaUser'
        db.delete_table(db.shorten_name(u'lumina_luminauser_groups'))

        # Removing M2M table for field user_permissions on 'LuminaUser'
        db.delete_table(db.shorten_name(u'lumina_luminauser_user_permissions'))

        # Deleting model 'Album'
        db.delete_table(u'lumina_album')

        # Removing M2M table for field shared_with on 'Album'
        db.delete_table(db.shorten_name(u'lumina_album_shared_with'))

        # Deleting model 'SharedAlbum'
        db.delete_table(u'lumina_sharedalbum')

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
        u'lumina.album': {
            'Meta': {'object_name': 'Album'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'shared_with': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'others_shared_albums'", 'blank': 'True', 'to': u"orm['lumina.LuminaUser']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['lumina.LuminaUser']"})
        },
        u'lumina.image': {
            'Meta': {'object_name': 'Image'},
            'album': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['lumina.Album']", 'null': 'True'}),
            'content_type': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.FileField', [], {'max_length': '300'}),
            'original_filename': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'size': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['lumina.LuminaUser']"})
        },
        u'lumina.imageselection': {
            'Meta': {'object_name': 'ImageSelection'},
            'album': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['lumina.Album']"}),
            'customer': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': u"orm['lumina.LuminaUser']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image_quantity': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'selected_images': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['lumina.Image']", 'symmetrical': 'False', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'W'", 'max_length': '1'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': u"orm['lumina.LuminaUser']"})
        },
        u'lumina.luminauser': {
            'Meta': {'object_name': 'LuminaUser'},
            'customer_of': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'customers'", 'null': 'True', 'to': u"orm['lumina.LuminaUser']"}),
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
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'user_type': ('django.db.models.fields.CharField', [], {'default': "'P'", 'max_length': '1'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'lumina.sharedalbum': {
            'Meta': {'object_name': 'SharedAlbum'},
            'album': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'shares_via_email'", 'to': u"orm['lumina.Album']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'random_hash': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '36'}),
            'shared_with': ('django.db.models.fields.EmailField', [], {'max_length': '254'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['lumina.LuminaUser']"})
        }
    }

    complete_apps = ['lumina']