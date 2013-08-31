# -*- coding: utf-8 -*-
#@PydevCodeAnalysisIgnore
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'Album'
        db.delete_table(u'lumina_album')

        # Removing M2M table for field shared_with on 'Album'
        db.delete_table(db.shorten_name(u'lumina_album_shared_with'))

        # Adding model 'Session'
        db.create_table(u'lumina_session', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=300)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['lumina.LuminaUser'])),
        ))
        db.send_create_signal(u'lumina', ['Session'])

        # Adding M2M table for field shared_with on 'Session'
        m2m_table_name = db.shorten_name(u'lumina_session_shared_with')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('session', models.ForeignKey(orm[u'lumina.session'], null=False)),
            ('luminauser', models.ForeignKey(orm[u'lumina.luminauser'], null=False))
        ))
        db.create_unique(m2m_table_name, ['session_id', 'luminauser_id'])


        # Changing field 'SharedAlbum.album'
        db.alter_column(u'lumina_sharedalbum', 'album_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['lumina.Session']))

        # Changing field 'Image.album'
        db.alter_column(u'lumina_image', 'album_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['lumina.Session'], null=True))

        # Changing field 'ImageSelection.album'
        db.alter_column(u'lumina_imageselection', 'album_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['lumina.Session']))

    def backwards(self, orm):
        # Adding model 'Album'
        db.create_table(u'lumina_album', (
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['lumina.LuminaUser'])),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=300)),
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

        # Deleting model 'Session'
        db.delete_table(u'lumina_session')

        # Removing M2M table for field shared_with on 'Session'
        db.delete_table(db.shorten_name(u'lumina_session_shared_with'))


        # Changing field 'SharedAlbum.album'
        db.alter_column(u'lumina_sharedalbum', 'album_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['lumina.Album']))

        # Changing field 'Image.album'
        db.alter_column(u'lumina_image', 'album_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['lumina.Album'], null=True))

        # Changing field 'ImageSelection.album'
        db.alter_column(u'lumina_imageselection', 'album_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['lumina.Album']))

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
        u'lumina.image': {
            'Meta': {'object_name': 'Image'},
            'album': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['lumina.Session']", 'null': 'True'}),
            'content_type': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.FileField', [], {'max_length': '300'}),
            'original_filename': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'size': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['lumina.LuminaUser']"})
        },
        u'lumina.imageselection': {
            'Meta': {'object_name': 'ImageSelection'},
            'album': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['lumina.Session']"}),
            'customer': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': u"orm['lumina.LuminaUser']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image_quantity': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'selected_images': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['lumina.Image']", 'symmetrical': 'False', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'W'", 'max_length': '1'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': u"orm['lumina.LuminaUser']"})
        },
        u'lumina.luminauser': {
            'Meta': {'object_name': 'LuminaUser'},
            'customer_of': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'customers'", 'null': 'True', 'to': u"orm['lumina.Studio']"}),
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
            'studio': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'photographers'", 'to': u"orm['lumina.Studio']"}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'user_type': ('django.db.models.fields.CharField', [], {'default': "'P'", 'max_length': '1'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'lumina.session': {
            'Meta': {'object_name': 'Session'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'shared_with': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'others_shared_albums'", 'blank': 'True', 'to': u"orm['lumina.LuminaUser']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['lumina.LuminaUser']"})
        },
        u'lumina.sharedalbum': {
            'Meta': {'object_name': 'SharedAlbum'},
            'album': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'shares_via_email'", 'to': u"orm['lumina.Session']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'random_hash': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '36'}),
            'shared_with': ('django.db.models.fields.EmailField', [], {'max_length': '254'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['lumina.LuminaUser']"})
        },
        u'lumina.studio': {
            'Meta': {'object_name': 'Studio'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['lumina']