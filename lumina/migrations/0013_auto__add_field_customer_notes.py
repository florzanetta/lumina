# -*- coding: utf-8 -*-
#@PydevCodeAnalysisIgnore
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Customer.notes'
        db.add_column(u'lumina_customer', 'notes',
                      self.gf('django.db.models.fields.TextField')(null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Customer.notes'
        db.delete_column(u'lumina_customer', 'notes')


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
            'address': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True', 'blank': 'True'}),
            'cuit': ('django.db.models.fields.CharField', [], {'max_length': '13', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ingresos_brutos': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'iva': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '1', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'notes': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
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
        u'lumina.sessionquote': {
            'Meta': {'object_name': 'SessionQuote'},
            'accepted_quote_alternative': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'on_delete': 'models.PROTECT', 'to': u"orm['lumina.SessionQuoteAlternative']"}),
            'accepted_rejected_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'accepted_rejected_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': u"orm['lumina.LuminaUser']"}),
            'cost': ('django.db.models.fields.DecimalField', [], {'max_digits': '10', 'decimal_places': '2'}),
            'customer': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'session_quotes'", 'to': u"orm['lumina.Customer']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image_quantity': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'Q'", 'max_length': '1'}),
            'studio': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'session_quotes'", 'to': u"orm['lumina.Studio']"}),
            'terms': ('django.db.models.fields.TextField', [], {})
        },
        u'lumina.sessionquotealternative': {
            'Meta': {'ordering': "['image_quantity']", 'unique_together': "(('session_quote', 'image_quantity'),)", 'object_name': 'SessionQuoteAlternative'},
            'cost': ('django.db.models.fields.DecimalField', [], {'max_digits': '10', 'decimal_places': '2'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image_quantity': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'session_quote': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'quote_alternatives'", 'to': u"orm['lumina.SessionQuote']"})
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