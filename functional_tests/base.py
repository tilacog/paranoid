import json
import os
import sys
import tempfile
import time
from datetime import datetime

from django.contrib.auth import get_user_model
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.ui import WebDriverWait

from jobs.models import report_filename

from .management.commands.create_session_cookie import create_session_cookie
from .server_tools import (create_media_file_on_server,
                           create_session_on_server, create_user_on_server,
                           reset_database, send_fixture_file)

DEFAULT_WAIT = 5
SCREEN_DUMP_LOCATION = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'screendumps'
)


class FunctionalTest(StaticLiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        for arg in sys.argv:
            if 'liveserver' in arg:
                cls.server_host = arg.split('=')[1]
                cls.server_url = 'http://' + cls.server_host
                cls.against_staging = True
                return
        super().setUpClass()
        cls.against_staging = False
        cls.server_url = cls.live_server_url

    @classmethod
    def tearDownClass(cls):
        if not cls.against_staging:
            super().tearDownClass()

    def setUp(self):
        if self.against_staging:
            reset_database(self.server_host)
        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(DEFAULT_WAIT)

    def tearDown(self):
        if self._test_has_failed():
            if not os.path.exists(SCREEN_DUMP_LOCATION):
                os.makedirs(SCREEN_DUMP_LOCATION)
            for ix, handle in enumerate(self.browser.window_handles):
                self._windowid = ix
                self.browser.switch_to_window(handle)
                self.take_screenshot()
                self.dump_html()
        self.browser.quit()
        super().tearDown

    def _test_has_failed(self):
        for method, error in self._outcome.errors:
            if error:
                return True
        return False

    def take_screenshot(self):
        filename = self._get_filename() + '.png'
        print('screenshotting to', filename)
        self.browser.get_screenshot_as_file(filename)

    def dump_html(self):
        filename = self._get_filename() + '.html'
        print('dumping page HTML to', filename)
        with open(filename, 'w') as f:
            f.write(self.browser.page_source)

    def _get_filename(self):
        timestamp = datetime.now().isoformat().replace(':', '.')[:19]
        path = '{folder}/{classname}.{method}-window{windowid}-{timestamp}'
        fmt_path = path.format(
            folder=SCREEN_DUMP_LOCATION,
            classname=self.__class__.__name__,
            method=self._testMethodName,
            windowid=self._windowid,
            timestamp=timestamp
        )

        return fmt_path

    def wait_for(self, function_with_assertion, timeout=DEFAULT_WAIT):
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                return function_with_assertion()
            except (AssertionError, WebDriverException):
                time.sleep(0.1)
        # one more try, which will raise any errors if they are outstanding
        return function_with_assertion()

    def wait_for_element_with_id(self, element_id):
        WebDriverWait(self.browser, timeout=30).until(
            lambda b: b.find_element_by_id(element_id),
            'Could not find element with id {}. Page text was:\n{}'.format(
                element_id, self.browser.find_element_by_tag_name('body').text
            )
        )

    def create_pre_authenticated_session(self, email, password):
        if self.against_staging:
            serialized_cookie = create_session_on_server(
                self.server_host, email, password
            )
            session_cookie = json.loads(serialized_cookie)
        else:
            session_cookie = create_session_cookie(email, password)

        self.browser.get(self.server_url + '/404/dont-exist/')
        self.browser.add_cookie(session_cookie)
        self.browser.refresh()

    def create_user(self, email, password):
        if self.against_staging:
            create_user_on_server(self.server_host, email, password)
        else:
            User = get_user_model()
            User.objects.create_user(email, password)

    def send_fixtures(self, app_name):
        if not self.against_staging:
            return  # nothing to do on local

        with tempfile.NamedTemporaryFile(
            suffix='.json',
            mode='w+'
        ) as fixture_file:
            call_command(
                'dumpdata',
                app_name,
                format='json',
                stdout=fixture_file
            )
            fixture_file.seek(0)
            assert os.path.exists(fixture_file.name)
            send_fixture_file(self.server_host, fixture_file.name)

    def assign_report_file_to_job_instance(self, job_instance, ext='.txt'):
        if self.against_staging:
            # Create file on server: /media/ dir
            file_name = report_filename(job_instance, None) + ext
            media_file_server_url = create_media_file_on_server(self.server_host, file_name)
            # Assign instance.report_file.name as on server
            job_instance.report_file.name = file_name

        else:
            # Assign a simple file
            job_instance.report_file = SimpleUploadedFile('test_file', b'test contents')

        job_instance.full_clean()
        job_instance.save()
