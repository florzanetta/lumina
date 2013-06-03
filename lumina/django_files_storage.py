'''
Created on Jun 3, 2013

@author: Horacio G. de Oro
'''
import os
import warnings
import logging

from django.core.files.storage import FileSystemStorage
from django.core.exceptions import SuspiciousOperation
from django.conf import settings

logger = logging.getLogger(__name__)

MEDIA_ROOT_FOR_TESTING = os.path.join(os.path.split(
    os.path.abspath(__file__))[0], '../test/test-images')


def _get_fallback_path(name):
    return os.path.join(MEDIA_ROOT_FOR_TESTING, name)


class TestImagesFallbackStorage(FileSystemStorage):

    def __init__(self):
        super(TestImagesFallbackStorage, self).__init__()
        if not settings.DEBUG:
            warnings.warn(
                "This Storage implementation is INSECURE "
                "and should be used ONLY if DEBUG is True")
            logger.warn("Using TestImagesFallbackStorage (it's INSECURE) with DEBUG = False")

    def path(self, name):
        # First, try with Django's implementation
        try:
            original_resolved_path = super(TestImagesFallbackStorage, self).path(name)
            if os.path.exists(original_resolved_path):
                return original_resolved_path
        except SuspiciousOperation:
            alternative_path = _get_fallback_path(name)
            if os.path.exists(alternative_path):
                logger.warn(
                    "path() raised SuspiciousOperation and alternative_path '%s' exists."
                    "Will return alternative_path",
                    alternative_path)
                return os.path.normpath(alternative_path)
            logger.warn(
                "path() raised SuspiciousOperation and alternative_path doesnt '%s' exists."
                "Will re-raise original SuspiciousOperation exception",
                alternative_path)
            raise

        # We get here if 'original_resolved_path' doesn't exists... will try fallback
        logger.warn(
            "path(): initial resolved path '%s' doesn't exists. Will try alternative",
            original_resolved_path)
        alternative_path = _get_fallback_path(name)
        if os.path.exists(alternative_path):
            logger.warn(
                "path() alternative_path '%s' does exists. Will return alternative_path",
                alternative_path)
            return os.path.normpath(alternative_path)
        logger.warn(
            "path() alternative_path '%s' does NOT exists either. "
            "Will return original_resolved_path '%s'", alternative_path, original_resolved_path)
        return original_resolved_path
