from django.urls import reverse

from general_test import ViewsTest


class IndexViewsTest(ViewsTest):
    def setUp(self):
        self.app = 'index'
        super().setUp()

    def test_view_status(self):
        self.info = {}
        codes_anonymous = [
            ['index'],
            #['login'],
            ['about'],
        ]
        codes_user = [
            #[['logout'], self.p_allowed],
            [['profile', None], self.p_all],
            [['feedbackForm', None], self.p_all],
            [['feedbackSubmit', None], self.p_all],
            [['feedbacklist', None], self.p_forbidden],  # god only
            [['feedbackconfirm', {'pk': 0}], self.p_forbidden],  # god only
            [['feedbackclose', {'pk': 0}], self.p_forbidden],  # god only
            [['changesettings', None], self.p_all],
            [['termsaccept', None], self.p_all],
            [['edit_tracks', None], self.p_support],
        ]

        # not logged in users. Ignore status, only use the views column of permission matrix.
        # Status should be 302 always.
        if self.debug:
            print("not logged in users")
        self.info['type'] = 'not logged in'
        for page in codes_anonymous:
            self.view_test_status(reverse(self.app+':'+page[0]), 200)
            # remove the page from the list of urls of this app.
            if page[0] in self.allurls: self.allurls.remove(page[0])

        for page, status in codes_user:
            self.view_test_status(reverse(self.app+':'+page[0], kwargs=page[1]), 302)

        # Test for users
        self.info['type'] = 'logged in'
        phases = range(1, 8)
        self.loop_phase_user(phases, codes_user)

        # check if all urls are processed, except login and logout
        self.assertListEqual(self.allurls, ['login', 'logout'], msg="Not all URLs of this app are tested!")


    def test_links_visible(self):
        """
        Test if all links shown in a view go to a page with status 200.
        Used to test if all visible menu items are actually available for the given user in the given view.

        :return:
        """
        self.info = {}
        skip = [reverse('professionalskills:filetypelist'), '/js_error_hook/'] #skip certain menu items that have a scenario which is too complicated to test for now
        views = ["index:index", 'index:profile']
        for phase in range(1,8):
            self.info['phase'] = str(phase)
            self.tp.Description = phase
            self.tp.save()
            for view in views:
                self.info['view'] = view
                ViewsTest.links_in_view_test(self, reverse(view), skip=skip)
