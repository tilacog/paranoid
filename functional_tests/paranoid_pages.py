from abc import ABCMeta, abstractmethod
from .page_objects import PageObject


class ParanoidPage(PageObject, metaclass=ABCMeta):
    """
    Very similar to PageObject, but implements common mehtods for all
    pages inside the Paranoid project.
    """

    @property
    def title(self):
        return self.browser.title

    @abstractmethod
    def check(self):
        """
        Use this method to assert if the browser really is visiting this page.
        """
        pass
