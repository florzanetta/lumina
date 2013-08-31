# -*- coding: utf-8 -*-
#@PydevCodeAnalysisIgnore
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'Image.album'
        db.delete_column(u'lumina_image', 'album_id')

        # Deleting field 'Image.user'
        db.delete_column(u'lumina_image', 'user_id')

        # Adding field 'Image.studio'
        db.add_column(u'lumina_image', 'studio',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['lumina.Studio']),
                      keep_default=False)

        # Adding field 'Image.session'
        db.add_column(u'lumina_image', 'session',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['lumina.Session'], null=True),
                      keep_default=False)

        # Deleting field 'ImageSelection.album'
        db.delete_column(u'lumina_imageselection', 'album_id')

        # Deleting field 'ImageSelection.user'
        db.delete_column(u'lumina_imageselection', 'user_id')

        # Adding field 'ImageSelection.studio'
        db.add_column(u'lumina_imageselection', 'studio',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=None, related_name='+', to=orm['lumina.Studio']),
                      keep_default=False)

        # Adding field 'ImageSelection.session'
        db.add_column(u'lumina_imageselection', 'session',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['lumina.Session']),
                      keep_default=False)


        # Changing field 'ImageSelection.customer'
        db.alter_column(u'lumina_imageselection', 'customer_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['lumina.Customer']))

    def backwards(self, orm):
        # Adding field 'Image.album'
        db.add_column(u'lumina_image', 'album',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['lumina.Session'], null=True),
                      keep_default=False)


        # User chose to not deal with backwards NULL issues for 'Image.user'
        raise RuntimeError("Cannot reverse this migration. 'Image.user' and its values cannot be restored.")
        # Deleting field 'Image.studio'
        db.delete_column(u'lumina_image', 'studio_id')

        # Deleting field 'Image.session'
        db.delete_column(u'lumina_image', 'session_id')


        # User chose to not deal with backwards NULL issues for 'ImageSelection.album'
        raise RuntimeError("Cannot reverse this migration. 'ImageSelection.album' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'ImageSelection.user'
        raise RuntimeError("Cannot reverse this migration. 'ImageSelection.user' and its values cannot be restored.")
        # Deleting field 'ImageSelection.studio'
        db.delete_column(u'lumina_imageselection', 'studio_id')

        # Deleting field 'ImageSelection.session'
        db.delete_column(u'lumina_imageselection', 'session_id')


        # Changing field 'ImageSelection.customer'
        db.alter_column(u'lumina_imageselection', 'customer_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['lumina.LuminaUser']))

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
            'customer_of': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'customers'", 'to': u"orm['lumina.Studio']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '20'})
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
            'user_for_studio': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'users'", 'null': 'True', 'to': u"orm['lumina.Studio']"}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'user_type': ('django.db.models.fields.CharField', [], {'default': "'P'", 'max_length': '1'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'lumina.session': {
            'Meta': {'object_name': 'Session'},
            'customer': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['lumina.Customer']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'shared_with': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'others_shared_albums'", 'blank': 'True', 'to': u"orm['lumina.LuminaUser']"}),
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