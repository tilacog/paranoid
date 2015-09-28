from .home_page import HomePage
from .page_objects import multi_page_element, page_element


class JobListPage(HomePage):

    return_home_button = page_element(id="id-return-home-btn")
    new_job_button = page_element(id="id-new-job-btn")

    @property
    def current_jobs(self):
        return self.browser.find_elements_by_css_selector('.job-row')

    @property
    def download_links(self):
        return self.browser.find_elements_by_css_selector('a.download-link')

    def check(self):
        self.test.assertTrue(self.return_home_button)
        self.test.assertTrue(self.new_job_button)

class JobDetailPage(HomePage):

    def check(self):
        pass
