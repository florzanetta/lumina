import logging
import traceback
import sys


class LoggingMiddleware(object):
    """
    Middleware that logs exceptions.
    """
    _middleware_logger = logging.getLogger('LoggingMiddleware')

    def process_exception(self, request, exception):
        try:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            out = traceback.format_exception(
                exc_type, exc_value, exc_traceback)
            self._middleware_logger.error("".join(out))
        except:
            self._middleware_logger.exception(
                "Exception detected while trying to report an exception. ")
