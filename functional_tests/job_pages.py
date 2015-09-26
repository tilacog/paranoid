from .home_page import HomePage
from .page_objects import multi_page_element, page_element


class JobListPage(HomePage):

    return_home_button = page_element(id="id_return_home_btn")
    new_job_button = page_element(id="id_new_job_btn")

    @property
    def current_jobs(self):
        return self.browser.find_elements_by_css_selector('.job_row')

    def check(self):
        self.test.assertTrue(self.return_home_button)
        self.test.assertTrue(self.new_job_button)

class JobDetailPage(HomePage):

    def check(self):
        pass
